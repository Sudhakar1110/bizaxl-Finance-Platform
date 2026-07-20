import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class CustomerCommunication(Document):
    def before_insert(self):
        if not self.sent_on:
            self.sent_on = now_datetime()

    def on_submit(self):
        self.update_delivery_status()

    def update_delivery_status(self):
        self.db_set("status", "Sent")
        self.db_set("delivery_status", "Sent")
