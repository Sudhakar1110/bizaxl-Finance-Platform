from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today

class FASTagRecharge(Document):
    def before_submit(self):
        self.status = "Completed"
        self.create_transaction()

    def create_transaction(self):
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "customer": self.customer,
            "transaction_type": "Payment",
            "transaction_category": "FASTag Recharge",
            "amount": self.recharge_amount,
            "description": f"FASTag Recharge for {self.vehicle_number}",
            "status": "Completed",
        })
        transaction.insert()
        transaction.submit()
        self.transaction_reference = transaction.name
