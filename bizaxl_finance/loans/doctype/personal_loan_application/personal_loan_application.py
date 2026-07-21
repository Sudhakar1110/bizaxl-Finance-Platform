import frappe
from frappe.model.document import Document
from frappe.utils import flt, today

class PersonalLoanApplication(Document):
    def validate(self):
        self.calculate_foir()
        self.validate_limits()

    def before_submit(self):
        self.status = "Approved"
        self.decision = "Auto-Approved"
        self.decision_date = today()

    def on_submit(self):
        self.create_disbursement()

    def calculate_foir(self):
        """Calculate FOIR (Fixed Obligation to Income Ratio)"""
        if self.monthly_income and self.monthly_income > 0:
            total_obligations = flt(self.existing_emi_obligations or 0)
            proposed_emi = self._estimate_emi()
            total_obligations += proposed_emi
            foir = (total_obligations / self.monthly_income) * 100
            self.scorecard_result = f"FOIR: {foir:.1f}%"

    def validate_limits(self):
        """Validate against product/policy limits"""
        if not self.loan_amount or not self.tenure_months:
            return

        max_amount = 2500000  # Rs. 25 lakhs default max
        max_tenure = 60       # 5 years

        if self.loan_amount > max_amount:
            frappe.throw(f"Personal loan amount cannot exceed Rs. {max_amount:,.0f}")
        if self.tenure_months > max_tenure:
            frappe.throw(f"Personal loan tenure cannot exceed {max_tenure} months")

    def create_disbursement(self):
        """Create loan disbursement on approval"""
        if self.status == "Approved" and self.disbursement_account:
            disbursement = frappe.get_doc({
                "doctype": "Loan Disbursement",
                "loan_application": self.name,
                "customer": self.customer,
                "disbursement_amount": self.loan_amount,
                "disbursement_date": self.disbursement_date or today(),
                "interest_rate": self.interest_rate,
                "tenure_months": self.tenure_months,
                "mode_of_payment": "Bank Transfer",
                "disbursement_account": self.disbursement_account,
            })
            disbursement.insert()
            disbursement.submit()
            self.disbursement_reference = disbursement.name

    def _estimate_emi(self):
        """Estimate monthly EMI for FOIR calculation"""
        if self.loan_amount and self.interest_rate and self.tenure_months:
            monthly_rate = flt(self.interest_rate) / 12 / 100
            tenure = flt(self.tenure_months)
            if monthly_rate > 0:
                import math
                emi = self.loan_amount * monthly_rate * math.pow(1 + monthly_rate, tenure) / \
                      (math.pow(1 + monthly_rate, tenure) - 1)
                return flt(emi)
            return flt(self.loan_amount / tenure)
        return 0
