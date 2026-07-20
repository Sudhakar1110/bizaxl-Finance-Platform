import frappe
from frappe.model.document import Document


class CompanyConfig(Document):
    def validate(self):
        if not self.company_name:
            frappe.throw("Company Name is required")

