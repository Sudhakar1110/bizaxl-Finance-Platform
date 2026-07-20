import frappe
from frappe.model.document import Document

class CustomerNomination(Document):
    def validate(self):
        self.validate_percentage_total()

    def validate_percentage_total(self):
        """Ensure total nomination percentage doesn't exceed 100%"""
        total = frappe.db.sql("""
            SELECT COALESCE(SUM(nominee_percentage), 0)
            FROM `tabCustomer Nomination`
            WHERE customer = %s AND name != %s
        """, (self.customer, self.name or "New"))[0][0]

        if float(total or 0) + float(self.nominee_percentage or 0) > 100:
            frappe.throw("Total nomination percentage cannot exceed 100%")
