from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LoanCollateral(Document):
    def validate(self):
        self.set_customer_from_loan()

    def set_customer_from_loan(self):
        if self.loan_application and not self.customer:
            loan = frappe.get_doc("Loan Application", self.loan_application)
            self.customer = loan.customer
