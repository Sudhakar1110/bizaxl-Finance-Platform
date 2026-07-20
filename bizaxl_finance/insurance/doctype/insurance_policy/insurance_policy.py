import frappe
from frappe.model.document import Document

class InsurancePolicy(Document):
    def validate(self):
        self.update_customer_insurance_total()

    def update_customer_insurance_total(self):
        total = frappe.db.sql("""
            SELECT COALESCE(SUM(sum_assured), 0)
            FROM `tabInsurance Policy`
            WHERE customer = %s AND status = 'Active' AND name != %s
        """, (self.customer, self.name or "New"))[0][0] + (self.sum_assured or 0)
        frappe.db.set_value("Bizaxl Customer", self.customer, "total_insurance", total)
