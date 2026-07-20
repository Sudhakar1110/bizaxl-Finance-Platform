from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months

class LoanDisbursement(Document):
    def validate(self):
        self.calculate_net_disbursement()

    def before_submit(self):
        self.status = "Disbursed"
        self.update_loan_application()
        self.create_transaction()

    def calculate_net_disbursement(self):
        fee = self.processing_fee_amount or 0
        gst = self.gst_amount or 0
        self.net_disbursement = (self.disbursement_amount or 0) - fee - gst
        self.total_emi_count = self.tenure_months

    def update_loan_application(self):
        loan_app = frappe.get_doc("Loan Application", self.loan_application)
        loan_app.disbursement_date = self.disbursement_date
        loan_app.first_emi_date = add_months(self.disbursement_date, 1)
        loan_app.status = "Disbursed"
        loan_app.save(ignore_permissions=True)

    def create_transaction(self):
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "customer": self.customer,
            "transaction_type": "Credit",
            "transaction_category": "Loan Disbursement",
            "amount": self.net_disbursement,
            "description": f"Loan disbursement - {self.loan_application}",
            "status": "Completed",
        })
        transaction.insert()
        transaction.submit()
        self.transaction_reference = transaction.name
