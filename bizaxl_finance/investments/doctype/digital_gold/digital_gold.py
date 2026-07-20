import frappe
from frappe.model.document import Document

class DigitalGold(Document):
    def validate(self):
        self.calculate_current_value()

    def calculate_current_value(self):
        if self.gold_grams and self.current_gold_rate:
            self.current_value = (self.gold_grams / 10) * self.current_gold_rate
        elif self.gold_grams and self.gold_rate_at_purchase:
            self.current_value = (self.gold_grams / 10) * self.gold_rate_at_purchase
