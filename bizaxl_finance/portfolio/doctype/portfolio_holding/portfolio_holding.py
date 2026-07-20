from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PortfolioHolding(Document):
    def validate(self):
        self.calculate_return()

    def calculate_return(self):
        if self.invested_amount and self.current_value and self.invested_amount > 0:
            self.return_percentage = ((self.current_value - self.invested_amount) / self.invested_amount) * 100

    def on_update(self):
        """Update customer's total investments"""
        total = frappe.db.sql("""
            SELECT COALESCE(SUM(current_value), 0)
            FROM `tabPortfolio Holding`
            WHERE customer = %s AND status = 'Active'
        """, self.customer)[0][0]
        frappe.db.set_value("Bizaxl Customer", self.customer, "total_investments", total)
