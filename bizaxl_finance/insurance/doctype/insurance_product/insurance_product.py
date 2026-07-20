from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InsuranceProduct(Document):
    def validate(self):
        self.validate_amounts()
        self.validate_ages()

    def validate_amounts(self):
        if self.min_sum_assured and self.max_sum_assured and self.min_sum_assured > self.max_sum_assured:
            frappe.throw("Minimum sum assured cannot exceed maximum sum assured")

    def validate_ages(self):
        if self.min_entry_age and self.max_entry_age and self.min_entry_age > self.max_entry_age:
            frappe.throw("Minimum entry age cannot exceed maximum entry age")
