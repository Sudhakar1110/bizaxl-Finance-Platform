from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PaymentMethod(Document):
    def validate(self):
        self.validate_amounts()

    def validate_amounts(self):
        if self.minimum_amount and self.maximum_amount:
            if self.minimum_amount > self.maximum_amount:
                frappe.throw("Minimum amount cannot be greater than maximum amount")
