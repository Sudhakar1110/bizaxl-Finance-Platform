from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CreditReport(Document):
    def validate(self):
        self.set_score_range()
        self.update_customer_score()

    def set_score_range(self):
        if self.credit_score:
            if self.credit_score >= 750:
                self.score_range = "Excellent (750-900)"
            elif self.credit_score >= 650:
                self.score_range = "Good (650-749)"
            elif self.credit_score >= 550:
                self.score_range = "Fair (550-649)"
            elif self.credit_score >= 400:
                self.score_range = "Poor (400-549)"
            else:
                self.score_range = "Very Poor (<400)"

    def update_customer_score(self):
        frappe.db.set_value("Bizaxl Customer", self.customer, "credit_score", self.credit_score)
