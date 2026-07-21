import frappe
from frappe.model.document import Document


class FundAccount(Document):
    """Track fund sources and availability for lending operations.
    
    Manages:
    - Own capital allocation
    - Borrowing lines
    - Co-lending partner funds
    - Securitization pools
    """
    
    def validate(self):
        self.calculate_balances()
    
    def calculate_balances(self):
        """Calculate available balance from allocated funds"""
        self.available_balance = (self.current_balance or 0) - (self.allocated_amount or 0)
    
    @staticmethod
    def get_total_available():
        """Get total available funds across all active accounts"""
        result = frappe.db.sql("""
            SELECT COALESCE(SUM(available_balance), 0) as total
            FROM `tabFund Account`
            WHERE is_active = 1
        """, as_dict=True)
        return result[0].total if result else 0
