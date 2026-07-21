import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months, add_days


class CSISApplication(Document):
    def validate(self):
        self.check_csis_eligibility()
        self.calculate_subsidy_string()
        self.set_submission_defaults()

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

        # Store subsidy info in remarks since subsidy_amount field not in DB
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
