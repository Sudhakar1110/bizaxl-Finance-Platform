import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime
import re

class BizaxlCustomer(Document):
    def validate(self):
        self.validate_pan()
        self.validate_mobile()
        self.validate_email()
        self.set_onboarding_details()

    def before_save(self):
        self.update_financial_summary()

    def validate_pan(self):
        if self.pan_number:
            pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            if not re.match(pan_pattern, self.pan_number):
                frappe.throw("Invalid PAN Number format. It should be 10 characters (e.g., ABCDE1234F)")

    def validate_mobile(self):
        if self.mobile_number:
            mobile_pattern = r'^[6-9]\d{9}$'
            if not re.match(mobile_pattern, self.mobile_number):
                frappe.throw("Invalid Mobile Number. Must be a valid 10-digit Indian mobile number.")

    def validate_email(self):
        if self.email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.email):
                frappe.throw("Invalid Email format.")

    def set_onboarding_details(self):
        if not self.onboarded_on:
            self.onboarded_on = now_datetime()
        if not self.onboarded_by:
            self.onboarded_by = frappe.session.user

    def update_financial_summary(self):
        """Update financial summary from related documents"""
        # Total balance from bank accounts
        bank_balance = frappe.db.sql("""
            SELECT COALESCE(SUM(current_balance), 0)
            FROM `tabBank Account`
            WHERE customer = %s AND docstatus = 1
        """, self.name)[0][0]
        self.total_balance = bank_balance

        # Total investments
        investment_value = frappe.db.sql("""
            SELECT COALESCE(SUM(current_value), 0)
            FROM `tabPortfolio Holding`
            WHERE customer = %s
        """, self.name)[0][0]
        self.total_investments = investment_value

        # Total loans outstanding
        loan_outstanding = frappe.db.sql("""
            SELECT COALESCE(SUM(outstanding_amount), 0)
            FROM `tabLoan Application`
            WHERE customer = %s AND status = 'Disbursed'
        """, self.name)[0][0]
        self.total_loans = loan_outstanding

        # Total insurance coverage
        insurance_coverage = frappe.db.sql("""
            SELECT COALESCE(SUM(sum_assured), 0)
            FROM `tabInsurance Policy`
            WHERE customer = %s AND status = 'Active'
        """, self.name)[0][0]
        self.total_insurance = insurance_coverage

    def get_dashboard_data(self):
        """Returns dashboard data for the customer portal"""
        return {
            "customer_name": self.customer_name,
            "total_balance": self.total_balance,
            "total_investments": self.total_investments,
            "total_loans": self.total_loans,
            "total_insurance": self.total_insurance,
            "credit_score": self.credit_score,
            "kyc_status": self.kyc_status,
            "recent_transactions": self.get_recent_transactions(),
            "upcoming_payments": self.get_upcoming_payments(),
            "investment_summary": self.get_investment_summary(),
        }

    def get_recent_transactions(self):
        return frappe.db.sql("""
            SELECT name, transaction_date, transaction_type, amount, description
            FROM `tabTransaction`
            WHERE customer = %s AND docstatus = 1
            ORDER BY transaction_date DESC
            LIMIT 10
        """, self.name, as_dict=True)

    def get_upcoming_payments(self):
        return frappe.db.sql("""
            SELECT name, due_date, bill_type, amount, provider
            FROM `tabBill Payment`
            WHERE customer = %s AND status = 'Pending'
            ORDER BY due_date ASC
            LIMIT 5
        """, self.name, as_dict=True)

    def get_investment_summary(self):
        return frappe.db.sql("""
            SELECT asset_class, COALESCE(SUM(current_value), 0) as total_value,
                   COALESCE(SUM(invested_amount), 0) as total_invested
            FROM `tabPortfolio Holding`
            WHERE customer = %s
            GROUP BY asset_class
        """, self.name, as_dict=True)
