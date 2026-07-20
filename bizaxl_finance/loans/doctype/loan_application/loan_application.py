import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_months, today
import math

class LoanApplication(Document):
    def validate(self):
        self.calculate_emi()
        self.set_loan_type()
        self.set_dates()

    def before_save(self):
        self.update_customer_loan_total()

    def calculate_emi(self):
        """Calculate EMI using PMT formula"""
        if self.loan_amount and self.interest_rate and self.tenure_months:
            principal = flt(self.loan_amount)
            monthly_rate = flt(self.interest_rate) / 12 / 100
            tenure = flt(self.tenure_months)

            if monthly_rate > 0:
                emi = principal * monthly_rate * math.pow(1 + monthly_rate, tenure) / \
                      (math.pow(1 + monthly_rate, tenure) - 1)
            else:
                emi = principal / tenure

            self.emi_amount = round(emi, 2)
            self.total_payable = round(emi * tenure, 2)
            self.total_interest = round(self.total_payable - principal, 2)

    def set_loan_type(self):
        if self.loan_product:
            loan_product = frappe.get_cached_value("Loan Product", self.loan_product, "loan_type")
            if loan_product:
                self.loan_type = loan_product

    def set_dates(self):
        if self.disbursement_date and self.tenure_months and not self.last_emi_date:
            self.last_emi_date = add_months(self.disbursement_date, self.tenure_months)

    def update_customer_loan_total(self):
        if self.status in ["Disbursed", "Approved"]:
            total_loans = frappe.db.sql("""
                SELECT COALESCE(SUM(loan_amount), 0)
                FROM `tabLoan Application`
                WHERE customer = %s AND status IN ('Disbursed', 'Approved')
            """, self.customer)[0][0]
            frappe.db.set_value("Bizaxl Customer", self.customer, "total_loans", total_loans)
