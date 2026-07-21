import frappe
from frappe.model.document import Document
from frappe.utils import flt

class DSAMaster(Document):
    def validate(self):
        self.validate_dsa_code()
        self.calculate_commission_outstanding()

    def validate_dsa_code(self):
        if self.dsa_code:
            existing = frappe.db.get_value("DSA Master", 
                {"dsa_code": self.dsa_code, "name": ["!=", self.name]}, "name")
            if existing:
                frappe.throw(f"DSA Code {self.dsa_code} already exists")

    def calculate_commission_outstanding(self):
        self.commission_outstanding = flt(self.total_commission_earned) - flt(self.commission_paid)
        if self.commission_outstanding < 0:
            self.commission_outstanding = 0

    def update_commission(self, amount):
        """Add commission earned to DSA's total"""
        self.total_commission_earned = flt(self.total_commission_earned) + flt(amount)
        self.calculate_commission_outstanding()
        self.save(ignore_permissions=True)

    def record_commission_payment(self, amount):
        """Record a commission payment made to DSA"""
        self.commission_paid = flt(self.commission_paid) + flt(amount)
        self.calculate_commission_outstanding()
        self.save(ignore_permissions=True)
