import json
import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, getdate, date_diff


class VehicleDetail(Document):
    def validate(self):
        self.calculate_ltv_by_category()
        self.validate_insurance()
        self.update_rc_tracker()
        self.set_valuation_defaults()

    def calculate_ltv_by_category(self):
        """Auto-calculate maximum LTV based on vehicle category per RBI norms"""
        ltv_limits = {
            "2 Wheeler": {"new": 90, "used": 80},
            "3 Wheeler": {"new": 85, "used": 75},
            "4 Wheeler - Hatchback": {"new": 85, "used": 75},
            "4 Wheeler - Sedan": {"new": 85, "used": 75},
            "4 Wheeler - SUV": {"new": 80, "used": 70},
            "Commercial Vehicle": {"new": 80, "used": 65},
            "Electric Vehicle": {"new": 85, "used": 75},
            "Tractor": {"new": 80, "used": 70},
        }

        limit = ltv_limits.get(self.vehicle_category, {"new": 80, "used": 70})
        is_new = self.condition == "New"
        max_ltv = limit.get("new" if is_new else "used", 80)

        if self.agreed_price and self.valuation_price:
            effective_price = min(self.agreed_price, self.valuation_price or self.agreed_price)
            max_loan = effective_price * max_ltv / 100

            # Calculate down payment percentage
            self._calculate_down_payment()

            frappe.msgprint(
                f"Max eligible loan: ₹{max_loan:,.2f} (LTV: {max_ltv}% of ₹{effective_price:,.2f})",
                alert=True
            )

    def validate_insurance(self):
        """Track insurance expiry and alert before 30 days"""
        if self.insurance_expiry:
            days_to_expiry = date_diff(getdate(self.insurance_expiry), getdate(today()))
            if 0 < days_to_expiry <= 30:
                frappe.msgprint(
                    f"⚠️ Insurance expiring on {self.insurance_expiry}. "
                    "Please renew to maintain coverage.",
                    alert=True, indicator="orange"
                )
            elif days_to_expiry <= 0:
                frappe.msgprint(
                    f"❌ Insurance EXPIRED on {self.insurance_expiry}. "
                    "Vehicle cannot be on road without valid insurance.",
                    alert=True, indicator="red"
                )

    def update_rc_tracker(self):
        """
        Full RC Hypothecation Tracking across stages:
        1. Pending → 2. Submitted to RTO → 3. Endorsed → 4. Copy Received → 5. Released

        Auto-updates dates based on status transitions.
        Tracks Parivahan API reference for integration.
        """
        # Auto-set dates based on status
        if self.rc_hypothecation_status == "Submitted to RTO":
            if not self.rc_submitted_date:
                self.rc_submitted_date = today()
            # Auto-update hypothecation date
            if not self.rc_hypothecation_date:
                self.rc_hypothecation_date = self.rc_submitted_date

        elif self.rc_hypothecation_status == "Endorsed":
            if not self.rc_endorsed_date:
                self.rc_endorsed_date = today()
            if self.rc_endorsed_date and self.rc_submitted_date:
                days_taken = date_diff(
                    getdate(self.rc_endorsed_date),
                    getdate(self.rc_submitted_date)
                )
                self.remarks = (self.remarks or "") + f"\nRTO endorsement took {days_taken} days."

        elif self.rc_hypothecation_status == "Copy Received":
            if not self.rc_received_date:
                self.rc_received_date = today()

        elif self.rc_hypothecation_status == "Released":
            if not self.rc_release_date:
                self.rc_release_date = today()

        # Initial submission from date
        if self.rc_hypothecation_date and not self.rc_hypothecation_status:
            self.rc_hypothecation_status = "Submitted to RTO"
            if not self.rc_submitted_date:
                self.rc_submitted_date = self.rc_hypothecation_date

        # Check for stuck status
        if self.rc_hypothecation_status == "Submitted to RTO" and self.rc_submitted_date:
            days_since_submission = date_diff(
                getdate(today()), getdate(self.rc_submitted_date)
            )
            if days_since_submission > 30:
                frappe.msgprint(
                    f"⚠️ RC submission pending for {days_since_submission} days. "
                    "Follow up with RTO/Parivahan.",
                    alert=True, indicator="orange"
                )

    def submit_to_parivahan(self):
        """
        Stub for Parivahan API integration.
        In production: call Parivahan/Vahan API for RC hypothecation.
        """
        # Parivahan API call stub
        api_response = {
            "status": "success",
            "application_number": f"PARV{today().replace('-', '')}{self.chassis_number[-4:] if self.chassis_number else '0000'}",
            "message": "Hypothecation application submitted to Parivahan",
            "submitted_at": str(today()),
            "rc_number": self.registration_number,
        }

        self.parivahan_reference = api_response["application_number"]
        self.parivahan_api_response = json.dumps(api_response, indent=2)
        self.rc_hypothecation_status = "Submitted to RTO"
        self.rc_submitted_date = today()
        self.rc_hypothecation_date = today()

        frappe.msgprint(
            f"✅ Submitted to Parivahan. Reference: {api_response['application_number']}",
            alert=True, indicator="green"
        )
        return api_response

    def check_parivahan_status(self):
        """
        Stub for Parivahan API status check.
        In production: call Parivahan/Vahan API to check RC status.
        """
        if not self.parivahan_reference:
            frappe.msgprint("No Parivahan reference found. Submit first.", alert=True)
            return

        # Stub: simulate status check
        status_response = {
            "reference": self.parivahan_reference,
            "current_status": self.rc_hypothecation_status,
            "last_updated": str(today()),
            "next_steps": "Awaiting RTO endorsement"
            if self.rc_hypothecation_status == "Submitted to RTO"
            else "Complete",
        }

        self.parivahan_api_response = json.dumps(status_response, indent=2)
        frappe.msgprint(
            f"Parivahan Status: {self.rc_hypothecation_status}",
            alert=True
        )

    def _calculate_down_payment(self):
        """Calculate down payment percentage based on agreed price"""
        if self.down_payment and self.agreed_price and self.agreed_price > 0:
            self.down_payment_percentage = round(
                (self.down_payment / self.agreed_price) * 100, 2
            )
            # Validate RBI minimum down payment norms
            min_down_payment = {
                "2 Wheeler": 10,
                "4 Wheeler - Hatchback": 15,
                "4 Wheeler - Sedan": 15,
                "4 Wheeler - SUV": 20,
                "Commercial Vehicle": 20,
                "Electric Vehicle": 15,
                "Tractor": 20,
            }
            required_min = min_down_payment.get(self.vehicle_category, 10)
            if self.down_payment_percentage < required_min:
                frappe.msgprint(
                    f"⚠️ Down payment of {self.down_payment_percentage}% is below "
                    f"minimum {required_min}% for {self.vehicle_category}.",
                    alert=True, indicator="orange"
                )

    def set_valuation_defaults(self):
        """Set valuation defaults"""
        if not self.valuation_price and self.otr_price:
            if self.condition == "New":
                self.valuation_price = self.otr_price
