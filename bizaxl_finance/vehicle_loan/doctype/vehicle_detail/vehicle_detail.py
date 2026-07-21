import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, getdate, date_diff


class VehicleDetail(Document):
    def validate(self):
        self.calculate_ltv_by_category()
        self.validate_insurance()
        self.check_rc_status()
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
                    f"Insurance expiring on {self.insurance_expiry}. "
                    "Please renew to maintain coverage."
                )

    def check_rc_status(self):
        """Update RC hypothecation status tracking"""
        if self.rc_hypothecation_date and not self.rc_hypothecation_status:
            self.rc_hypothecation_status = "Submitted to RTO"

    def set_valuation_defaults(self):
        """Set valuation defaults"""
        if not self.valuation_price and self.otr_price:
            if self.condition == "New":
                self.valuation_price = self.otr_price
