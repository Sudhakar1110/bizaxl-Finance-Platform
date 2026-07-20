import frappe
from frappe.model.document import Document
from frappe.utils import today

class LoanRepayment(Document):
    def validate(self):
        self.validate_amount()
        self.get_outstanding_balance()

    def validate_amount(self):
        if not self.amount or self.amount <= 0:
            frappe.throw("Repayment amount must be greater than zero")

    def before_submit(self):
        self.status = "Completed"
        self.create_transaction()
        self.update_loan_application()

    def get_outstanding_balance(self):
        loan = frappe.get_doc("Loan Application", self.loan_application)
        total_paid = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0)
            FROM `tabLoan Repayment`
            WHERE loan_application = %s AND docstatus = 1 AND name != %s
        """, (self.loan_application, self.name or "New"))[0][0]
        self.outstanding_balance = max(0, loan.loan_amount - total_paid - (self.amount or 0))

    def create_transaction(self):
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "customer": self.customer,
            "transaction_type": "Debit",
            "transaction_category": "Loan Repayment",
            "amount": self.amount,
            "description": f"Loan repayment - {self.loan_application} (EMI #{self.emi_number})",
            "status": "Completed",
        })
        transaction.insert()
        transaction.submit()
        self.transaction_reference = transaction.name

    def update_loan_application(self):
        if self.outstanding_balance <= 0:
            frappe.db.set_value("Loan Application", self.loan_application, "status", "Closed")
