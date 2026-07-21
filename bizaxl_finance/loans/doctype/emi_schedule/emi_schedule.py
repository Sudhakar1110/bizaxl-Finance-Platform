import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_months, today
import math

class EMISchedule(Document):
    def validate(self):
        self.validate_emi()
        self.calculate_outstanding()

    def validate_emi(self):
        if not self.emi_amount or self.emi_amount <= 0:
            frappe.throw("EMI amount must be greater than zero")

    def calculate_outstanding(self):
        """Calculate outstanding principal after this EMI"""
        if self.loan_application and self.emi_number:
            loan = frappe.get_cached_value("Loan Application",
                self.loan_application, ["loan_amount", "tenure_months"], as_dict=True)

            if not loan:
                return

            # Get total principal paid so far (excluding this EMI)
            total_paid = frappe.db.sql("""
                SELECT COALESCE(SUM(principal_amount), 0)
                FROM `tabEMI Schedule`
                WHERE loan_application = %s
                    AND emi_number < %s
                    AND docstatus < 2
            """, (self.loan_application, self.emi_number))[0][0]

            self.outstanding_principal = flt(loan.loan_amount - total_paid - (self.principal_amount or 0))

    @staticmethod
    def generate_schedule(loan_application, disbursement_date, loan_amount, interest_rate, tenure_months):
        """Generate full EMI schedule for a loan"""
        existing = frappe.db.exists("EMI Schedule", {"loan_application": loan_application})
        if existing:
            return

        monthly_rate = flt(interest_rate) / 12 / 100
        if monthly_rate > 0:
            emi = loan_amount * monthly_rate * math.pow(1 + monthly_rate, tenure_months) / \
                  (math.pow(1 + monthly_rate, tenure_months) - 1)
        else:
            emi = loan_amount / tenure_months

        emi = round(emi, 2)
        outstanding = loan_amount

        for i in range(1, tenure_months + 1):
            interest = round(outstanding * monthly_rate, 2) if monthly_rate > 0 else 0
            principal = round(emi - interest, 2)

            if i == tenure_months:
                principal = outstanding
                emi = principal + interest

            schedule = frappe.get_doc({
                "doctype": "EMI Schedule",
                "loan_application": loan_application,
                "emi_number": i,
                "due_date": add_months(disbursement_date, i),
                "emi_amount": emi,
                "principal_amount": principal,
                "interest_amount": interest,
                "outstanding_principal": max(0, outstanding - principal),
                "status": "Pending"
            })
            schedule.insert(ignore_permissions=True)

            outstanding -= principal
            if outstanding <= 0:
                break
