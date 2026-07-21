import math
import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, add_months


class CSISApplication(Document):
    def validate(self):
        self.check_csis_eligibility()
        self.calculate_subsidy_string()
        self.set_submission_defaults()
        self.calculate_step_up_emi()

    def check_csis_eligibility(self):
        """Check CSIS eligibility: family income up to Rs.8L"""
        if self.family_income and self.family_income <= 800000:
            self.eligible_for_csis = 1
            if self.family_income <= 450000:
                self.income_slab = "Up to Rs.4.5L"
            elif self.family_income <= 800000:
                self.income_slab = "Rs.4.5L - Rs.8L"
        else:
            self.eligible_for_csis = 0
            self.income_slab = "Above Rs.8L"

    def calculate_subsidy_string(self):
        """Calculate interest subsidy and store description in remarks"""
        if not self.eligible_for_csis:
            return

        if self.income_slab == "Up to Rs.4.5L":
            subsidy = self.get_full_subsidy()
        elif self.income_slab == "Rs.4.5L - Rs.8L":
            subsidy = self.get_partial_subsidy()
        else:
            subsidy = 0

        subsidy_note = f"Eligible Subsidy: ₹{subsidy:,.2f}"
        if self.remarks:
            if subsidy_note not in self.remarks:
                self.remarks += f"\n{subsidy_note}"
        else:
            self.remarks = subsidy_note

    def get_full_subsidy(self):
        """Full interest subsidy during moratorium (up to Rs.4.5L)"""
        return 50000  # Placeholder - calc from linked loan in production

    def get_partial_subsidy(self):
        """Partial interest subsidy for higher income slab"""
        return 20000  # Placeholder

    def set_submission_defaults(self):
        if self.eligible_for_csis and not self.submission_date:
            self.submission_date = today()
        if self.eligible_for_csis and not self.subsidy_status:
            self.subsidy_status = "Pending"

    def calculate_step_up_emi(self):
        """
        Calculate Step-up EMI schedule for education loan repayment.

        After moratorium period (course + 6 months), repayment starts with:
        - Year 1: Initial EMI (lower, post-graduation income)
        - Each subsequent year: EMI increases by step_up_percentage%

        Formula:
        Year N EMI = Year 1 EMI * (1 + step_up_percentage/100) ^ (N-1)

        Example (10% step-up):
        Year 1: ₹10,000
        Year 2: ₹11,000
        Year 3: ₹12,100
        Year 4: ₹13,310
        Year 5: ₹14,641
        """
        if not self.loan_amount or not self.interest_rate or not self.tenanture_months:
            return

        principal = flt(self.loan_amount)
        annual_rate = flt(self.interest_rate) / 100
        tenure_months = flt(self.tenanture_months)
        step_up = flt(self.step_up_percentage or 10) / 100
        moratorium = flt(self.moratorium_months or 6)

        if tenure_months <= 0:
            return

        # Calculate standard EMI using PMT formula
        monthly_rate = annual_rate / 12
        if monthly_rate > 0:
            standard_emi = (principal * monthly_rate *
                math.pow(1 + monthly_rate, tenure_months)) / \
                (math.pow(1 + monthly_rate, tenure_months) - 1)
        else:
            standard_emi = principal / tenure_months

        # Step-up: Year 1 EMI is lower than standard
        # Standard EMI covers full loan over full tenure
        # Step-up starts lower and increases

        # For a step-up loan, we calculate the effective initial EMI
        # such that the total NPV equals the loan amount
        # Simplified: Year 1 = 70% of standard EMI, then step up
        initial_emi = standard_emi * 0.70

        self.initial_emi = round(initial_emi, 2)

        # Calculate EMIs for years 1-5
        emi_years = []
        for year in range(5):
            year_emi = initial_emi * math.pow(1 + step_up, year)
            emi_years.append(round(year_emi, 2))

        # Map to fields (at least 5 years for display)
        self.year_2_emi = emi_years[1] if len(emi_years) > 1 else 0
        self.year_3_emi = emi_years[2] if len(emi_years) > 2 else 0
        self.year_4_emi = emi_years[3] if len(emi_years) > 3 else 0
        self.year_5_emi = emi_years[4] if len(emi_years) > 4 else 0

        # Add step-up schedule to remarks
        schedule = (
            f"\n📊 Step-up EMI Schedule:\n"
            f"  Moratorium: {int(moratorium)} months\n"
            f"  Step-up: {self.step_up_percentage or 10}% per year\n"
            f"  Year 1: ₹{self.initial_emi:,.2f}/mo\n"
            f"  Year 2: ₹{self.year_2_emi:,.2f}/mo\n"
            f"  Year 3: ₹{self.year_3_emi:,.2f}/mo\n"
            f"  Year 4: ₹{self.year_4_emi:,.2f}/mo\n"
            f"  Year 5: ₹{self.year_5_emi:,.2f}/mo"
        )
        if self.remarks:
            self.remarks += schedule
        else:
            self.remarks = schedule
