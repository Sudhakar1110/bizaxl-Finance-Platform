import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months


class GoldPledge(Document):
    def validate(self):
        self.set_maturity_date()
        self.calculate_gold_totals()
        self.calculate_ltv()
        self.set_valuation_defaults()

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
                frappe.msgprint(
                    f"Warning: LTV ratio {self.ltv_ratio}% exceeds RBI maximum of 75%. "
                    f"Maximum eligible: ₹{self.total_gold_value * 0.75:,.2f}"
                )
                self.db_set("status", "Top-Up Available")
                self._log_ltv_breach()

    def set_valuation_defaults(self):
        if not self.valuation_date:
            self.valuation_date = today()
        if not self.disbursement_date:
            self.disbursement_date = today()

    def _log_ltv_breach(self):
        """Log LTV breach as a customer communication alert"""
        if not self.name:
            return
        try:
            frappe.get_doc({
                "doctype": "Customer Communication",
                "customer": self.name,
                "subject": "LTV Breach Alert - Gold Loan",
                "message_body": (
                    f"Your Gold Loan LTV ratio is {self.ltv_ratio}%. "
                    f"This exceeds the regulatory limit. Please make a partial repayment "
                    f"or pledge additional gold to maintain compliance."
                ),
                "channel": "App Notification",
                "communication_type": "Alert",
                "status": "Draft",
                "reference_doctype": "Gold Pledge",
                "reference_name": self.name,
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to create LTV breach alert: {e}", "Gold Pledge")

    def on_submit(self):
        pass  # LTV monitoring handled via scheduler


def daily_ltv_monitoring():
    """Daily task: Monitor LTV for all active gold loans"""
    active_loans = frappe.get_all("Gold Pledge",
        filters={"status": ["in", ["Active", "Top-Up Available"]]},
        fields=["name", "loan_amount", "ltv_ratio", "customer_name"]
    )

    for loan in active_loans:
        # In production: fetch live MCX rate and re-calculate LTV
        # live_rate = get_mcx_gold_rate()
        if loan.ltv_ratio and loan.ltv_ratio > 75:
            try:
                frappe.get_doc({
                    "doctype": "Customer Communication",
                    "customer": loan.name,
                    "subject": "Daily LTV Alert - Action Required",
                    "message_body": (
                        f"Your Gold Loan LTV is {loan.ltv_ratio}%. "
                        f"Please contact branch for options."
                    ),
                    "channel": "App Notification",
                    "communication_type": "Alert",
                    "status": "Draft",
                    "reference_doctype": "Gold Pledge",
                    "reference_name": loan.name,
                }).insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Daily LTV alert failed for {loan.name}: {e}", "Gold LTV Monitor")
