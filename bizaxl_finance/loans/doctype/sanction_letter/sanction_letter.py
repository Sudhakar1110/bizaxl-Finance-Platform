import frappe
from frappe.model.document import Document
from frappe.utils import today, flt

class SanctionLetter(Document):
    def validate(self):
        self.calculate_fees()
        self.validate_amounts()

    def before_submit(self):
        self.status = "Approved"
        self.update_loan_application()

    def before_cancel(self):
        self.status = "Draft"

    def calculate_fees(self):
        if self.sanctioned_amount and self.processing_fee_percent:
            self.processing_fee_amount = flt(self.sanctioned_amount * self.processing_fee_percent / 100)
            self.gst_on_processing_fee = flt(self.processing_fee_amount * 0.18)

    def validate_amounts(self):
        if self.sanctioned_amount <= 0:
            frappe.throw("Sanctioned amount must be greater than zero")

    def update_loan_application(self):
        frappe.db.set_value("Loan Application", self.loan_application, {
            "status": "Approved",
            "approval_date": self.sanction_date or today(),
            "approved_by": self.sanctioned_by
        })
