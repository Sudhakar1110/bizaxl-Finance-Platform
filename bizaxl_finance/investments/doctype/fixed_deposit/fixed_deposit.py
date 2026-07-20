from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_months, today, date_diff
import math

class FixedDeposit(Document):
    def validate(self):
        self.calculate_maturity()
        self.update_status_based_on_maturity()

    def calculate_maturity(self):
        if self.deposit_date and self.tenure_months:
            self.maturity_date = add_months(self.deposit_date, self.tenure_months)

        if self.deposit_amount and self.interest_rate and self.tenure_months:
            if self.interest_type == "Simple":
                interest = (self.deposit_amount * self.interest_rate * self.tenure_months) / (12 * 100)
                self.maturity_amount = self.deposit_amount + interest
            elif self.interest_type == "Compounded":
                self.maturity_amount = self.deposit_amount * math.pow(
                    1 + (self.interest_rate / (12 * 100)), self.tenure_months
                )
            elif self.interest_type == "Cumulative":
                quarterly_rate = self.interest_rate / (4 * 100)
                quarters = math.floor(self.tenure_months / 3)
                self.maturity_amount = self.deposit_amount * math.pow(1 + quarterly_rate, quarters)

    def update_status_based_on_maturity(self):
        if self.maturity_date and self.maturity_date < today() and self.status == "Active":
            self.status = "Matured"
