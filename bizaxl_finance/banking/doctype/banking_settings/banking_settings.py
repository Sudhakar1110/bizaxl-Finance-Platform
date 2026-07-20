from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BankingSettings(Document):
    def validate(self):
        self.validate_limits()

    def validate_limits(self):
        if self.max_upi_per_transaction > self.max_upi_daily:
            frappe.throw("Per transaction limit cannot exceed daily limit")
