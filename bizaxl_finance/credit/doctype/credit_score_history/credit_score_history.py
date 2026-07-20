from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CreditScoreHistory(Document):
    def validate(self):
        self.set_previous_score()

    def set_previous_score(self):
        last_score = frappe.db.get_value("Bizaxl Customer", self.customer, "credit_score")
        if last_score:
            self.previous_score = last_score
