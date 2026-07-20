from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CreditGoal(Document):
    def validate(self):
        self.set_current_score()

    def set_current_score(self):
        score = frappe.db.get_value("Bizaxl Customer", self.customer, "credit_score")
        if score:
            self.current_score = score
            if self.current_score >= self.target_score:
                self.status = "Achieved"
