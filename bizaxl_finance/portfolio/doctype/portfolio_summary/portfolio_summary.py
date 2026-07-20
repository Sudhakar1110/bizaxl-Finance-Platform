import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class PortfolioSummary(Document):
    def validate(self):
        self.calculate_summary()

    def calculate_summary(self):
        if not self.customer:
            return

        holdings = frappe.db.sql("""
            SELECT 
                asset_type,
                COALESCE(SUM(invested_amount), 0) as total_invested,
                COALESCE(SUM(current_value), 0) as total_current
            FROM `tabPortfolio Holding`
            WHERE customer = %s AND status = 'Active'
            GROUP BY asset_type
        """, self.customer, as_dict=True)

        total_invested = 0
        total_current = 0
        type_totals = {}

        for h in holdings:
            total_invested += h.total_invested
            total_current += h.total_current
            type_totals[h.asset_type] = h.total_current

        self.total_invested = total_invested
        self.total_current_value = total_current
        self.total_returns = total_current - total_invested
        if total_invested > 0:
            self.return_percentage = (self.total_returns / total_invested) * 100
        self.last_updated = now_datetime()
