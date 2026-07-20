import frappe
from frappe.model.document import Document


class InterestRateEngine(Document):
    def validate(self):
        self.effective_rate = (self.base_rate or 0) + (self.spread or 0)

