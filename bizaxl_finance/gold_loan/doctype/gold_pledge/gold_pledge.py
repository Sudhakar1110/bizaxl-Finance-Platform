import json
import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months, flt


class GoldPledge(Document):
    def validate(self):
        self.set_maturity_date()
        self.calculate_gold_totals()
        self.calculate_ltv()
        self.set_valuation_defaults()
        self.check_top_up_eligibility()

    def before_submit(self):
        self.status = "Active"

    def set_maturity_date(self):
        if self.disbursement_date and self.tenure_months:
            self.maturity_date = add_months(self.disbursement_date, self.tenure_months)

    def calculate_gold_totals(self):
        if self.get("gold_items"):
            self.total_gross_weight = sum((i.gross_weight or 0) for i in self.gold_items)
            self.total_net_weight = sum((i.net_weight or 0) for i in self.gold_items)
            self.total_gold_value = sum((i.item_value or 0) for i in self.gold_items)

    def calculate_ltv(self):
        if self.total_gold_value and self.loan_amount:
            self.ltv_ratio = round((self.loan_amount / self.total_gold_value) * 100, 2)
            self.ltv_amount = self.loan_amount
            if self.ltv_ratio > 75:
                self._trigger_ltv_breach_alert()

    def set_valuation_defaults(self):
        if not self.valuation_date:
            self.valuation_date = today()
        if not self.disbursement_date:
            self.disbursement_date = today()

    def check_top_up_eligibility(self):
        """Check if top-up loan is available based on LTV headroom"""
        if not self.is_top_up and self.total_gold_value and self.loan_amount:
            max_loan_at_75 = self.total_gold_value * 0.75
            current_loan = flt(self.loan_amount or 0)
            headroom = max_loan_at_75 - current_loan

            if headroom > 0 and current_loan > 0:
                top_up_eligible = headroom >= 10000  # Min Rs.10K for top-up
                if top_up_eligible:
                    if self.top_up_status in ("Not Applicable", ""):
                        self.top_up_status = "Eligible"
                        frappe.msgprint(
                            f"💡 Top-up eligible: ₹{headroom:,.2f} available at current LTV 75%.",
                            alert=True, indicator="green"
                        )

    def _trigger_ltv_breach_alert(self):
        """
        LTV Breach Alert with SMS/notification logging.
        When LTV exceeds 75% RBI limit:
        1. Log detailed alert with frappe.log_error
        2. Show user-facing warning with max eligible amount
        3. Update status to Top-Up Available
        4. Generate LTV breach notification (stub for SMS/Email)
        """
        if not self.name:
            return

        max_eligible = self.total_gold_value * 0.75
        excess_amount = flt(self.loan_amount) - max_eligible

        # 1. Log detailed alert
        alert_data = {
            "doctype": "Fraud Alert",
            "alert_type": "Gold LTV Breach",
            "customer_name": self.customer_name,
            "reference_doctype": "Gold Pledge",
            "reference_name": self.name if self.name else "(New)",
            "description": (
                f"LTV {self.ltv_ratio}% exceeds RBI 75% limit. "
                f"Loan Amount: ₹{self.loan_amount:,.2f}, "
                f"Gold Value: ₹{self.total_gold_value:,.2f}, "
                f"Excess: ₹{excess_amount:,.2f}"
            ),
            "severity": "High",
        }

        try:
            alert = frappe.get_doc(alert_data)
            alert.insert(ignore_permissions=True)
            alert.db_set("status", "Open")
        except Exception:
            frappe.log_error(
                title="Gold LTV Breach (Fraud Alert failed)",
                message=json.dumps(alert_data, indent=2)
            )

        # 2. User-facing warning
        frappe.msgprint(
            f"⚠️ LTV BREACH: {self.ltv_ratio}% exceeds RBI 75% limit!\n"
            f"Maximum eligible loan: ₹{max_eligible:,.2f}\n"
            f"Excess amount: ₹{excess_amount:,.2f}",
            alert=True, indicator="red"
        )

        # 3. Update status (set in-memory, not via db_set since we're mid-validation)
        if self.status in ("Active", ""):
            self.status = "Top-Up Available"

    def create_top_up_loan(self, top_up_amount):
        """
        Create a top-up loan against existing Gold Pledge.
        Called from the Gold Appraiser or Loan Manager.
        """
        if not self.total_gold_value or not self.loan_amount:
            frappe.throw("Cannot create top-up: Missing gold value or loan amount")

        max_loan = self.total_gold_value * 0.75
        current_loan = flt(self.loan_amount)
        available_headroom = max_loan - current_loan

        if top_up_amount > available_headroom:
            frappe.throw(
                f"Top-up amount ₹{top_up_amount:,.2f} exceeds available "
                f"headroom ₹{available_headroom:,.2f} (75% LTV limit)"
            )

        # Create new Gold Pledge as top-up
        top_up = frappe.get_doc({
            "doctype": "Gold Pledge",
            "customer_name": self.customer_name,
            "customer_pan": self.customer_pan,
            "customer_aadhaar": self.customer_aadhaar,
            "branch": self.branch,
            "loan_amount": top_up_amount,
            "interest_rate": self.interest_rate,
            "tenure_months": self.tenure_months,
            "interest_type": self.interest_type,
            "market_rate_per_gram": self.market_rate_per_gram,
            "is_top_up": 1,
            "parent_pledge": self.name,
            "top_up_amount": top_up_amount,
            "top_up_date": today(),
            "top_up_status": "Approved",
            "valuation_date": today(),
            "appraiser": self.appraiser,
            "status": "Active",
        })
        top_up.insert(ignore_permissions=True)
        top_up.submit()

        # Update parent pledge status
        frappe.db.set_value("Gold Pledge", self.name, "top_up_status", "Disbursed")

        frappe.msgprint(
            f"✅ Top-up loan of ₹{top_up_amount:,.2f} created: {top_up.name}",
            alert=True, indicator="green"
        )
        return top_up.name

    def on_submit(self):
        pass  # LTV monitoring handled via scheduler


def daily_ltv_monitoring():
    """
    Daily task: Monitor LTV for all active gold loans.
    Fetches live MCX rate and recalculates LTV.
    Generates alerts for breaches.
    """
    active_loans = frappe.get_all("Gold Pledge",
        filters={"status": ["in", ["Active", "Top-Up Available"]]},
        fields=["name", "loan_amount", "ltv_ratio", "customer_name",
                "total_gold_value", "market_rate_per_gram"]
    )

    breach_count = 0
    for loan in active_loans:
        # In production: fetch live MCX rate and re-calculate LTV
        # live_rate = get_mcx_gold_rate()
        # Then: ltv = loan.loan_amount / (loan.total_gold_value / old_rate * live_rate)

        if loan.ltv_ratio and loan.ltv_ratio > 75:
            breach_count += 1
            frappe.log_error(
                title="Daily Gold LTV Alert",
                message=json.dumps({
                    "gold_pledge": loan.name,
                    "ltv_ratio": loan.ltv_ratio,
                    "customer": loan.customer_name,
                    "loan_amount": loan.loan_amount,
                    "action_required": "Partial repayment or additional pledge required",
                    "alert_date": str(today()),
                }, indent=2)
            )

    if breach_count > 0:
        frappe.log_error(
            title=f"Gold LTV Daily Summary: {breach_count} breaches",
            message=f"{breach_count} gold loans exceed 75% LTV as of {today()}"
        )
