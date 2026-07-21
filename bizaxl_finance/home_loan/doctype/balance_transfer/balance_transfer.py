import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

class BalanceTransfer(Document):
    def validate(self):
        self.calculate_amounts()
        self.validate_amounts()

    def before_save(self):
        self.calculate_net_disbursement()

    def calculate_amounts(self):
        """Calculate new EMI and net disbursement"""
        if self.new_loan_amount and self.new_interest_rate and self.new_tenure_months:
            self.new_monthly_emi = self._calculate_emi(
                self.new_loan_amount,
                self.new_interest_rate,
                self.new_tenure_months
            )

    def calculate_net_disbursement(self):
        """Net disbursement = new loan - old outstanding - processing fee"""
        net = flt(self.new_loan_amount)
        net -= flt(self.old_outstanding_amount)
        net -= flt(self.total_processing_fee)

        if self.transfer_type == "Balance Transfer with Top-Up":
            net += flt(self.top_up_amount)

        self.net_disbursement_amount = net if net > 0 else 0

    def validate_amounts(self):
        """Validate transfer amounts"""
        if self.new_loan_amount and self.old_outstanding_amount:
            if self.new_loan_amount < self.old_outstanding_amount:
                frappe.throw(
                    "New loan amount must be at least the old outstanding amount"
                )

    def _calculate_emi(self, principal, annual_rate, tenure_months):
        """Calculate EMI using standard formula"""
        monthly_rate = (annual_rate / 100) / 12
        if monthly_rate == 0:
            return flt(principal / tenure_months)
        emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
        emi /= ((1 + monthly_rate) ** tenure_months - 1)
        return flt(emi)

    def on_submit(self):
        """On submit, create disbursement record"""
        if self.net_disbursement_amount and self.net_disbursement_amount > 0:
            disbursement = frappe.get_doc({
                "doctype": "Loan Disbursement",
                "loan_application": self.loan_application,
                "disbursement_date": self.disbursement_date or today(),
                "disbursed_amount": self.net_disbursement_amount,
                "disbursement_mode": "NEFT",
            })
            disbursement.insert(ignore_permissions=True)
            self.db_set("top_up_disbursed", 1)
