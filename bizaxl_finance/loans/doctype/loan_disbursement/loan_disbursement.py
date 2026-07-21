import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months, flt


class LoanDisbursement(Document):
    def validate(self):
        self.auto_fetch_processing_fee()
        self.calculate_net_disbursement()

    def before_submit(self):
        self.status = "Disbursed"
        self.update_loan_application()
        self.create_transaction()

    def auto_fetch_processing_fee(self):
        """Auto-fetch processing fee percentage from Loan Product"""
        if not self.processing_fee_percentage and self.loan_application:
            loan_app = frappe.get_cached_value(
                "Loan Application", self.loan_application, "loan_product"
            )
            if loan_app:
                fee_rate = frappe.get_cached_value(
                    "Loan Product", loan_app, "processing_fee_percentage"
                ) or 2.0  # Default 2% if not configured
                self.processing_fee_percentage = flt(fee_rate)

        # Auto-calculate fee amount from percentage
        if self.processing_fee_percentage and self.disbursement_amount:
            fee_pct = flt(self.processing_fee_percentage)
            self.processing_fee_amount = round(
                flt(self.disbursement_amount) * fee_pct / 100, 2
            )
            # GST @ 18% on processing fee
            self.gst_amount = round(self.processing_fee_amount * 0.18, 2)

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
