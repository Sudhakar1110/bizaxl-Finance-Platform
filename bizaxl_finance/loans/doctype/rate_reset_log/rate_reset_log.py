import frappe
from frappe.model.document import Document
from frappe.utils import today

class RateResetLog(Document):
    def validate(self):
        self.validate_rates()
        self.check_notification()

    def before_submit(self):
        self.apply_rate_change()

    def validate_rates(self):
        if self.previous_rate == self.new_rate:
            frappe.throw("New rate must be different from previous rate")
        if self.new_rate < 0:
            frappe.throw("Interest rate cannot be negative")

    def check_notification(self):
        """Flag if customer needs to be notified per RBI norms"""
        if abs(self.new_rate - self.previous_rate) >= 0.5:
            self.notified_to_customer = 0

    def apply_rate_change(self):
        """Update the loan application with new rate"""
        if self.loan_application:
            frappe.db.set_value("Loan Application", self.loan_application,
                "interest_rate", self.new_rate)
