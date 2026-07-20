import frappe
from frappe.model.document import Document


class NBFCLoanApplication(Document):
    def validate(self):
        if self.loan_amount and self.interest_rate and self.tenure_months:
            self.calculate_emi()
    def calculate_emi(self):
        import math
        p = self.loan_amount; r = (self.interest_rate or 0) / 12 / 100; n = self.tenure_months or 1
        self.emi_amount = round(p * r * (1+r)**n / ((1+r)**n - 1), 2) if r > 0 else round(p/n, 2)

