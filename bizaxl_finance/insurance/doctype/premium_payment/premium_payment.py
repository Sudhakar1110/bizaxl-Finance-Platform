from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PremiumPayment(Document):
    def validate(self):
        self.set_customer_from_policy()

    def before_submit(self):
        self.status = "Paid"
        self.create_transaction()

    def set_customer_from_policy(self):
        if self.insurance_policy and not self.customer:
            policy = frappe.get_doc("Insurance Policy", self.insurance_policy)
            self.customer = policy.customer

    def create_transaction(self):
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "customer": self.customer,
            "transaction_type": "Debit",
            "transaction_category": "Insurance Premium",
            "amount": self.premium_amount,
            "description": f"Insurance premium payment for {self.insurance_policy}",
            "status": "Completed",
        })
        transaction.insert()
        transaction.submit()
        self.receipt_number = transaction.name
