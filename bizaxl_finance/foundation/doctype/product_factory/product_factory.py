import json
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ProductFactory(Document):
    def validate(self):
        self.validate_interest_rates()
        self.validate_amount_tenure()

    def validate_interest_rates(self):
        if self.min_interest_rate and self.max_interest_rate:
            if self.min_interest_rate > self.max_interest_rate:
                frappe.throw("Minimum interest rate cannot exceed maximum interest rate")

        if self.rate_slabs_json:
            try:
                slabs = json.loads(self.rate_slabs_json)
                if isinstance(slabs, list):
                    for slab in slabs:
                        if slab.get("rate", 0) < self.min_interest_rate or \
                           slab.get("rate", 0) > self.max_interest_rate:
                            frappe.throw(
                                f"Slab rate {slab.get('rate')}% outside configured "
                                f"range ({self.min_interest_rate}-{self.max_interest_rate}%)"
                            )
            except json.JSONDecodeError:
                frappe.msgprint("Invalid JSON in Rate Slabs", indicator="orange")

    def validate_amount_tenure(self):
        if self.min_loan_amount and self.max_loan_amount:
            if self.min_loan_amount > self.max_loan_amount:
                frappe.throw("Minimum loan amount exceeds maximum")
        if self.min_tenure_months and self.max_tenure_months:
            if self.min_tenure_months > self.max_tenure_months:
                frappe.throw("Minimum tenure exceeds maximum")

    def check_eligibility(self, applicant, amount=None, tenure=None):
        """Check if applicant is eligible for this product
        
        Args:
            applicant: dict with age, credit_score, monthly_income
            amount: requested loan amount
            tenure: requested tenure in months
        
        Returns:
            dict with eligible, reasons list, max_eligible_amount
        """
        reasons = []

        # Age check
        age = applicant.get("age", 0)
        if age < (self.min_age or 0):
            reasons.append(f"Minimum age {self.min_age} not met (current: {age})")
        if age > (self.max_age or 999):
            reasons.append(f"Exceeds maximum age {self.max_age}")

        # Credit score
        score = applicant.get("credit_score", 0)
        if score < (self.min_credit_score or 0):
            reasons.append(f"Credit score {score} below minimum {self.min_credit_score}")

        # Income
        income = applicant.get("monthly_income", 0)
        if income < (self.min_monthly_income or 0):
            reasons.append(f"Monthly income {income} below minimum {self.min_monthly_income}")

        # Amount
        if amount:
            if amount < (self.min_loan_amount or 0):
                reasons.append(f"Amount below minimum {self.min_loan_amount}")
            if amount > (self.max_loan_amount or 0):
                reasons.append(f"Amount exceeds maximum {self.max_loan_amount}")

        # Tenure
        if tenure:
            if tenure < (self.min_tenure_months or 1):
                reasons.append(f"Tenure below minimum {self.min_tenure_months} months")
            if tenure > (self.max_tenure_months or 999):
                reasons.append(f"Tenure exceeds maximum {self.max_tenure_months} months")

        max_amount = min(
            self.max_loan_amount or float("inf"),
            flt(income * (self.income_multiple or 1)) if self.income_multiple else float("inf")
        )

        return {
            "eligible": len(reasons) == 0,
            "reasons": reasons,
            "max_eligible_amount": max_amount,
            "product": self.name,
        }

    def calculate_emi(self, principal, annual_rate, tenure_months):
        """Calculate EMI for this product"""
        monthly_rate = (annual_rate / 100) / 12
        if monthly_rate == 0:
            return flt(principal / tenure_months)
        emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
        emi /= ((1 + monthly_rate) ** tenure_months - 1)
        return flt(emi)
