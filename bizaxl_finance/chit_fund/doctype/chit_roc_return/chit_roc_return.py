import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

class ChitROCReturn(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_filing()

    def before_submit(self):
        self.status = "Filed"
        self.filing_date = today()

    def calculate_totals(self):
        self.net_balance = flt(self.total_receipts - self.total_payments)
        self.closing_balance = flt(
            (self.opening_balance or 0) + self.net_balance
        )

    def validate_filing(self):
        if not self.filing_authority:
            frappe.throw("Filing authority is required before submission")

    @staticmethod
    def populate_from_chit_group(chit_group_name, return_type="Monthly Return"):
        """Pre-populate a ROC return from chit group data"""
        chit = frappe.get_cached_value("Chit Group", chit_group_name,
            ["chit_value", "number_of_members", "chit_name"], as_dict=True)

        if not chit:
            frappe.throw(f"Chit Group {chit_group_name} not found")

        subscribers = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'Prized' THEN 1 ELSE 0 END) as prized,
                SUM(CASE WHEN status = 'Defaulting' THEN 1 ELSE 0 END) as defaulting
            FROM `tabChit Subscriber`
            WHERE chit_group = %s
        """, chit_group_name, as_dict=True)[0]

        return {
            "chit_group": chit_group_name,
            "return_type": return_type,
            "total_subscribers": subscribers.total or 0,
            "active_subscribers": subscribers.active or 0,
            "prized_subscribers": subscribers.prized or 0,
            "defaulting_subscribers": subscribers.defaulting or 0,
            "total_subscriptions_collected": flt(chit.chit_value),
        }
