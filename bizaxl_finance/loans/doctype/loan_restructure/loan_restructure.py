import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

class LoanRestructure(Document):
    def validate(self):
        self.validate_terms()
        self.calculate_impact()

    def before_submit(self):
        self.approval_status = "Approved"
        self.approval_date = today()
        self.status = "Active"
        self.update_loan_terms()

    def on_cancel(self):
        self.status = "Draft"
        self.approval_status = "Pending"

    def validate_terms(self):
        if self.new_interest_rate and self.new_interest_rate < 0:
            frappe.throw("Interest rate cannot be negative")
        if self.new_tenure_months and self.new_tenure_months < 1:
            frappe.throw("Tenure must be at least 1 month")

    def calculate_impact(self):
        if self.current_outstanding and self.new_outstanding:
            self.concession_amount = flt(self.current_outstanding - self.new_outstanding)

    def update_loan_terms(self):
        if self.loan_application:
            loan = frappe.get_doc("Loan Application", self.loan_application)
            if self.new_interest_rate:
                loan.interest_rate = self.new_interest_rate
            if self.new_tenure_months:
                loan.tenure_months = self.new_tenure_months
            loan.save(ignore_permissions=True)
            frappe.db.set_value("Loan Application", self.loan_application,
                "status", "Disbursed")
