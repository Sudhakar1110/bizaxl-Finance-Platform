from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class MutualFund(Document):
    def validate(self):
        self.calculate_current_value()
        self.calculate_returns()

    def before_save(self):
        self.last_updated = now_datetime()

    def calculate_current_value(self):
        if self.units_held and self.nav:
            self.current_value = self.units_held * self.nav

    def calculate_returns(self):
        if self.invested_amount and self.current_value and self.invested_amount > 0:
            self.abs_return = ((self.current_value - self.invested_amount) / self.invested_amount) * 100
