from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today

class MobileRecharge(Document):
    def before_submit(self):
        self.status = "Completed"
        self.payment_date = today()
        self.create_transaction()

    def create_transaction(self):
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "customer": self.customer,
            "transaction_type": "Payment",
            "transaction_category": "Mobile Recharge",
            "amount": self.plan_amount,
            "description": f"Mobile Recharge - {self.operator} ({self.mobile_number})",
            "status": "Completed",
        })
        transaction.insert()
        transaction.submit()
        self.transaction_reference = transaction.name
