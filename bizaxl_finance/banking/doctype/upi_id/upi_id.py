from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class UPIID(Document):
    def validate(self):
        self.validate_upi_format()
        self.set_primary_flag()

    def validate_upi_format(self):
        if self.upi_id:
            # Basic UPI format validation: something@provider
            import re
            if not re.match(r'^[\w.-]+@[\w.-]+$', self.upi_id):
                frappe.throw("Invalid UPI ID format. It should be in format: username@bank")

    def set_primary_flag(self):
        if self.is_primary:
            frappe.db.sql("""
                UPDATE `tabUPI ID`
                SET is_primary = 0
                WHERE customer = %s AND name != %s
            """, (self.customer, self.name or "New"))

            # Update customer's primary UPI ID
            frappe.db.set_value("Bizaxl Customer", self.customer,
                "primary_upi_id", self.upi_id)

            # Update bank account
            frappe.db.set_value("Bank Account", self.bank_account, "upi_id", self.upi_id)
