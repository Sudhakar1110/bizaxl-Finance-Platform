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
        """Log LTV breach. Gold Pledge has no direct Bizaxl Customer link,
        so we log via frappe.log_error for manual review."""
        if not self.name:
            return
        frappe.log_error(
            title="Gold LTV Breach",
            message=(
                f"Gold Pledge {self.name}: LTV {self.ltv_ratio}% exceeds 75%.\n"
                f"Customer: {self.customer_name}, Amount: {self.loan_amount}"
            )
        )
        # Also set a user-friendly message
        frappe.msgprint(
            f"⚠️ LTV Breach logged for {self.customer_name}. "
            f"LTV ratio {self.ltv_ratio}% exceeds RBI 75% limit.",
            alert=True, indicator="red"
        )

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
            frappe.log_error(
                title="Daily Gold LTV Alert",
                message=(
                    f"Gold Pledge {loan.name}: LTV {loan.ltv_ratio}% exceeds 75%.\n"
                    f"Customer: {loan.customer_name}, Amount: {loan.loan_amount}"
                )
            )
