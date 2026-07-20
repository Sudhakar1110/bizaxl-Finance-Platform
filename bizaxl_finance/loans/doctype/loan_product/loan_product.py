import frappe
from frappe.model.document import Document

class LoanProduct(Document):
    def validate(self):
        self.validate_amounts()
        self.validate_tenure()

    def validate_amounts(self):
        if self.min_amount and self.max_amount and self.min_amount > self.max_amount:
            frappe.throw("Minimum amount cannot exceed maximum amount")

    def validate_tenure(self):
        if self.min_tenure_months and self.max_tenure_months and self.min_tenure_months > self.max_tenure_months:
            frappe.throw("Minimum tenure cannot exceed maximum tenure")
