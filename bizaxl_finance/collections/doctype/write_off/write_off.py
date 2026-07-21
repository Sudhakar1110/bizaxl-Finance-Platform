import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

class WriteOff(Document):
    def validate(self):
        self.calculate_amounts()
        self.validate_approval()

    def before_submit(self):
        self.status = "Approved"

    def on_submit(self):
        self.execute_write_off()

    def calculate_amounts(self):
        if self.loan_application:
            loan = frappe.get_cached_value("Loan Application",
                self.loan_application, ["loan_amount", "interest_rate"], as_dict=True)

            if not loan:
                return

            total_paid = frappe.db.sql("""
                SELECT COALESCE(SUM(amount), 0)
                FROM `tabLoan Repayment`
                WHERE loan_application = %s AND docstatus = 1
            """, self.loan_application)[0][0]

            self.outstanding_principal = flt(loan.loan_amount - total_paid)
            self.total_outstanding = flt(
                self.outstanding_principal
                + (self.accrued_interest or 0)
                + (self.penalty_amount or 0)
            )
            self.write_off_amount = flt(
                self.total_outstanding - (self.recovery_amount_realized or 0)
            )
            self.net_impact = flt(
                self.write_off_amount - (self.provision_held_amount or 0)
            )

    def validate_approval(self):
        if not self.approved_by and self.docstatus == 1:
            frappe.throw("Write-off must be approved by an authorized user")

    def execute_write_off(self):
        """Mark the loan and NPA as written off"""
        if self.loan_application:
            frappe.db.set_value("Loan Application", self.loan_application,
                "status", "Written Off")

        if self.npa_classification:
            frappe.db.set_value("NPA Classification", self.npa_classification,
                "status", "Written Off")
