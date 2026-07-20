from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime

class KYCDocument(Document):
    def validate(self):
        self.validate_expiry()
        self.update_customer_kyc_status()

    def validate_expiry(self):
        if self.expiry_date and self.expiry_date < today():
            frappe.throw(f"Document {self.document_type} has already expired on {self.expiry_date}")

    def before_save(self):
        if self.verification_status == "Verified" and not self.verified_on:
            self.verified_on = now_datetime()
            self.verified_by = frappe.session.user
            self.is_verified = 1

    def update_customer_kyc_status(self):
        """Update customer's overall KYC status based on document verification"""
        if self.verification_status == "Verified":
            customer = frappe.get_doc("Bizaxl Customer", self.customer)
            if customer.kyc_status == "Pending":
                customer.db_set("kyc_status", "Under Review")
