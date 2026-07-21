import json
import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime

class CreditCommitteeDecision(Document):
    def validate(self):
        self.set_loan_details()
        self.validate_committee_level()

    def before_submit(self):
        self.approved_by = frappe.session.user
        self.approved_on = now_datetime()
        self.update_loan_application()

    def set_loan_details(self):
        """Auto-fetch loan details from the application"""
        if self.loan_application:
            loan = frappe.get_doc("Loan Application", self.loan_application)
            self.loan_amount = loan.loan_amount
            if not self.customer:
                self.customer = loan.customer

    def validate_committee_level(self):
        """Validate committee level based on loan amount slabs"""
        if self.loan_amount:
            slabs = [
                (0, 500000, "Branch Manager"),
                (500000, 2500000, "Regional Credit"),
                (2500000, 10000000, "HO Credit Committee"),
                (10000000, float("inf"), "Board"),
            ]
            for min_amt, max_amt, level in slabs:
                if min_amt <= self.loan_amount < max_amt:
                    if self.committee_level != level:
                        frappe.msgprint(
                            f"Recommended committee level for ₹{self.loan_amount:,.0f} is: {level}",
                            indicator="orange"
                        )
                    break

    def update_loan_application(self):
        """Update loan application status based on decision"""
        if not self.loan_application:
            return

        loan = frappe.get_doc("Loan Application", self.loan_application)

        if self.decision == "Approve" or self.decision == "Approve with Conditions":
            loan.status = "Approved"
            loan.approval_date = self.decision_date or today()
            loan.approved_by = frappe.session.user
        elif self.decision == "Reject":
            loan.status = "Rejected"
            loan.rejection_reason = self.remarks
        elif self.decision == "Refer to Higher Committee":
            loan.status = "Under Review"

        if self.sanctioned_amount:
            loan.loan_amount = self.sanctioned_amount

        loan.save(ignore_permissions=True)

    def on_cancel(self):
        """Handle cancellation - revert loan application if needed"""
        if self.loan_application:
            loan = frappe.get_doc("Loan Application", self.loan_application)
            loan.status = "Under Review"
            loan.save(ignore_permissions=True)
