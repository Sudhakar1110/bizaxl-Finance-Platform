import frappe
from frappe.model.document import Document


class GLSettings(Document):
    """Central accounting configuration for loan portfolio.
    
    Maps loan transactions to ERPNext Chart of Accounts:
    - Loan Receivable → Asset (Loan Portfolio)
    - Interest Income → Income (Interest Earned)
    - Bank → Asset (Disbursement/Collection)
    - Provision → Liability/Expense (NPA)
    """
    
    def validate(self):
        self.validate_accounts()
    
    def validate_accounts(self):
        """Verify that configured accounts exist in the Chart of Accounts"""
        account_fields = [
            "loan_receivable_account",
            "interest_income_account",
            "disbursement_bank_account",
            "interest_receivable_account",
            "npa_provision_account",
            "provision_expense_account",
        ]
        for field in account_fields:
            ac = getattr(self, field, None)
            if ac and not frappe.db.exists("Account", ac):
                frappe.msgprint(
                    f"Warning: Account '{ac}' does not exist in Chart of Accounts. "
                    f"Please create it first.",
                    alert=True
                )
    
    def get_loan_accounts(self):
        """Return all configured loan accounts as a dict"""
        return {
            "loan_receivable": self.loan_receivable_account,
            "interest_receivable": self.interest_receivable_account,
            "interest_income": self.interest_income_account,
            "processing_fee": self.processing_fee_account,
            "disbursement_bank": self.disbursement_bank_account,
            "repayment_bank": self.repayment_bank_account or self.disbursement_bank_account,
            "npa_provision": self.npa_provision_account,
            "provision_expense": self.provision_expense_account,
        }
