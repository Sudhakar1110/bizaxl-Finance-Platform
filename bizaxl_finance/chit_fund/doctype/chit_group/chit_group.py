import frappe
from frappe.model.document import Document


class ChitGroup(Document):
    def validate(self):
        if self.chit_value and self.number_of_members:
            self.monthly_subscription = self.chit_value / self.number_of_members
        if self.start_date and self.duration_months:
            self.expected_end_date = frappe.utils.add_months(self.start_date, self.duration_months)
        if self.chit_value and self.foreman_commission:
            self.foreman_commission_amount = self.chit_value * (self.foreman_commission or 5) / 100

