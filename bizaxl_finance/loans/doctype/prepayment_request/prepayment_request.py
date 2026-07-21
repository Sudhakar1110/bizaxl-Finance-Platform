import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

class PrepaymentRequest(Document):
    def validate(self):
        self.get_outstanding()
        self.calculate_prepayment()

    def before_submit(self):
        self.status = "Approved"
        self.approved_date = today()

    def on_submit(self):
        self.update_loan_application()
        self.create_repayment()

    def get_outstanding(self):
        if self.loan_application:
            loan = frappe.get_cached_value("Loan Application",
                self.loan_application, "loan_amount")

            total_repaid = frappe.db.sql("""
                SELECT COALESCE(SUM(amount), 0)
                FROM `tabLoan Repayment`
                WHERE loan_application = %s AND docstatus = 1
            """, self.loan_application)[0][0]

            self.outstanding_balance = flt(loan - total_repaid)

    def calculate_prepayment(self):
        if self.requested_amount <= 0:
            frappe.throw("Prepayment amount must be greater than zero")

        if self.prepayment_type == "Full Prepayment (Foreclosure)":
            self.requested_amount = self.outstanding_balance

        self.principal_reduction = flt(self.requested_amount)
        self.prepayment_penalty_amount = flt(
            self.requested_amount * (self.prepayment_penalty_percent or 0) / 100
        )
        self.new_outstanding_balance = flt(
            self.outstanding_balance - self.principal_reduction
        )
        self.approved_amount = self.requested_amount

    def create_repayment(self):
        """Create a Loan Repayment record for this prepayment"""
        if self.approved_amount and self.approved_amount > 0:
            repayment_type = "Foreclosure" if self.prepayment_type == "Full Prepayment (Foreclosure)" else "Partial Prepayment"
            repayment = frappe.get_doc({
                "doctype": "Loan Repayment",
                "loan_application": self.loan_application,
                "customer": self.customer,
                "repayment_type": repayment_type,
                "amount": self.approved_amount,
                "payment_date": self.effective_date or today(),
                "penalty_amount": self.prepayment_penalty_amount or 0,
                "status": "Completed",
            })
            repayment.insert()
            repayment.submit()

    def update_loan_application(self):
        if self.new_outstanding_balance <= 0:
            frappe.db.set_value("Loan Application", self.loan_application, "status", "Closed")
