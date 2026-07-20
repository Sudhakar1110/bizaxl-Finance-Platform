from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InsuranceNominee(Document):
    def validate(self):
        self.validate_percentage()

    def validate_percentage(self):
        if self.insurance_policy:
            total = frappe.db.sql("""
                SELECT COALESCE(SUM(percentage), 0)
                FROM `tabInsurance Nominee`
                WHERE insurance_policy = %s AND name != %s
            """, (self.insurance_policy, self.name or "New"))[0][0]
            if float(total or 0) + float(self.percentage or 0) > 100:
                frappe.throw("Total nominee percentage cannot exceed 100%")
