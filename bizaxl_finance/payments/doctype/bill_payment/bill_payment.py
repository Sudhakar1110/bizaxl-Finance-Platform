from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today

class BillPayment(Document):
    def validate(self):
        self.calculate_total()
        self.check_overdue()

    def before_submit(self):
        self.status = "Paid"
        self.payment_date = today()
        self.create_transaction()

    def calculate_total(self):
        self.total_amount = (self.amount or 0) + (self.late_fee or 0) - (self.discount or 0)

    def check_overdue(self):
        if self.due_date and self.due_date < today() and self.status == "Pending":
            self.status = "Overdue"

    def create_transaction(self):
        """Create a transaction record for the bill payment"""
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "customer": self.customer,
            "transaction_type": "Payment",
            "transaction_category": "Bill Payment",
            "amount": self.total_amount,
            "description": f"Payment of {self.bill_type} bill - {self.provider} ({self.bill_number})",
            "status": "Completed",
            "reference_number": f"BP{self.name}",
        })
        transaction.insert()
        transaction.submit()
        self.transaction_reference = transaction.name
