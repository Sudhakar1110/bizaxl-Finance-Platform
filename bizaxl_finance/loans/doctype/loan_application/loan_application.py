import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_months, today
import math


class LoanApplication(Document):
    def validate(self):
        self.calculate_emi()
        self.set_loan_type()
        self.set_dates()
        self.calculate_risk_grade()

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

    def calculate_risk_grade(self):
        """
        Calculate Risk Grade (A1-D) based on credit score, LTV, and loan amount.

        Score -> Grade mapping:
          A1: 80-100 (Excellent)
          A2: 70-79  (Very Good)
          B1: 60-69  (Good)
          B2: 50-59  (Satisfactory)
          C1: 40-49  (Fair)
          C2: 30-39  (Below Average)
          D:  0-29   (Poor)

        Risk Score = (Credit Score Factor * 0.4) + (LTV Factor * 0.3) + (Amount Factor * 0.3)
        """
        # Default values
        credit_score = flt(self.credit_score or 750)
        ltv_ratio = flt(getattr(self, 'ltv_ratio', 0)) or 0
        loan_amount = flt(self.loan_amount or 0)

        # 1. Credit Score Factor (0-100)
        if credit_score >= 800:
            credit_factor = 100
        elif credit_score >= 750:
            credit_factor = 80
        elif credit_score >= 700:
            credit_factor = 65
        elif credit_score >= 650:
            credit_factor = 50
        elif credit_score >= 600:
            credit_factor = 35
        elif credit_score >= 550:
            credit_factor = 20
        else:
            credit_factor = 10

        # 2. LTV Factor (0-100) - lower LTV is better
        if ltv_ratio <= 40:
            ltv_factor = 100
        elif ltv_ratio <= 50:
            ltv_factor = 80
        elif ltv_ratio <= 60:
            ltv_factor = 60
        elif ltv_ratio <= 70:
            ltv_factor = 40
        elif ltv_ratio <= 80:
            ltv_factor = 20
        else:
            ltv_factor = 10

        # 3. Amount Factor (0-100) - smaller loans are lower risk
        if loan_amount <= 500000:
            amount_factor = 100
        elif loan_amount <= 1000000:
            amount_factor = 80
        elif loan_amount <= 2500000:
            amount_factor = 60
        elif loan_amount <= 5000000:
            amount_factor = 40
        elif loan_amount <= 10000000:
            amount_factor = 20
        else:
            amount_factor = 10

        # Composite risk score
        risk_score = (credit_factor * 0.4) + (ltv_factor * 0.3) + (amount_factor * 0.3)
        self.risk_score = round(risk_score, 2)

        # Map score to grade
        if risk_score >= 80:
            self.risk_grade = "A1"
        elif risk_score >= 70:
            self.risk_grade = "A2"
        elif risk_score >= 60:
            self.risk_grade = "B1"
        elif risk_score >= 50:
            self.risk_grade = "B2"
        elif risk_score >= 40:
            self.risk_grade = "C1"
        elif risk_score >= 30:
            self.risk_grade = "C2"
        else:
            self.risk_grade = "D"

        # Auto-set assessment date if not set
        if not self.risk_assessment_date:
            self.risk_assessment_date = today()

        # Auto-populate remarks
        grade_meaning = {
            "A1": "Excellent - Auto-approve up to Rs.10L",
            "A2": "Very Good - Auto-approve up to Rs.5L",
            "B1": "Good - Standard processing",
            "B2": "Satisfactory - Enhanced due diligence",
            "C1": "Fair - Credit committee approval required",
            "C2": "Below Average - Committee approval + higher rate",
            "D": "Poor - Recommend rejection",
        }
        risk_note = grade_meaning.get(self.risk_grade, "")
        if self.risk_grading_remarks:
            if risk_note not in self.risk_grading_remarks:
                self.risk_grading_remarks += f"\n{risk_note}"
        else:
            self.risk_grading_remarks = risk_note

        # Auto-set committee workflow based on risk grade
        if self.risk_grade in ("C1", "C2", "D"):
            frappe.msgprint(
                f"⚠️ Risk Grade {self.risk_grade} requires Credit Committee approval.",
                alert=True, indicator="orange"
            )

    def update_customer_loan_total(self):
        if self.status in ["Disbursed", "Approved"]:
            total_loans = frappe.db.sql("""
                SELECT COALESCE(SUM(loan_amount), 0)
                FROM `tabLoan Application`
                WHERE customer = %s AND status IN ('Disbursed', 'Approved')
            """, self.customer)[0][0]
            frappe.db.set_value("Bizaxl Customer", self.customer, "total_loans", total_loans)
