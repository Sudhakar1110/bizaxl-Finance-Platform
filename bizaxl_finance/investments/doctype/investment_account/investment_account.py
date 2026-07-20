from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InvestmentAccount(Document):
    def validate(self):
        self.update_customer_investment_total()

    def update_customer_investment_total(self):
        frappe.db.set_value("Bizaxl Customer", self.customer, "total_investments",
            frappe.db.sql("""
                SELECT COALESCE(SUM(current_value), 0)
                FROM `tabInvestment Account`
                WHERE customer = %s AND status = 'Active'
            """, self.customer)[0][0])
