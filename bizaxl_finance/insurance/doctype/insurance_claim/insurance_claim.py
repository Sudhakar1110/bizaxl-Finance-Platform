from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InsuranceClaim(Document):
    def validate(self):
        self.set_customer_from_policy()

    def set_customer_from_policy(self):
        if self.insurance_policy and not self.customer:
            policy = frappe.get_doc("Insurance Policy", self.insurance_policy)
            self.customer = policy.customer
