from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, today

class FinancialGoal(Document):
    def validate(self):
        self.calculate_progress()

    def calculate_progress(self):
        if self.target_amount and self.target_amount > 0:
            total_savings = self.current_savings or 0
            
            # Calculate from portfolio holdings
            holdings = frappe.db.get_all("Portfolio Holding",
                filters={"customer": self.customer, "status": "Active"},
                fields=["current_value"])
            
            for h in holdings:
                total_savings += h.current_value or 0

            self.current_progress = min(100, (total_savings / self.target_amount) * 100)
            
            # Calculate required monthly saving
            if self.target_date and self.target_amount:
                days_left = date_diff(self.target_date, today())
                months_left = max(1, days_left / 30)
                remaining = self.target_amount - total_savings
                if remaining > 0 and months_left > 0:
                    self.monthly_saving_required = remaining / months_left

            if self.current_progress >= 100:
                self.status = "Achieved"
