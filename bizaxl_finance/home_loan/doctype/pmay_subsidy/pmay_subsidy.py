import frappe
from frappe.model.document import Document


class PMAYSubsidy(Document):
    def validate(self):
        self.check_eligibility()
        self.calculate_subsidy()

    def before_save(self):
        if not self.eligible_for_clss:
            self.eligible_for_clss = 0
        if not self.subsidy_status:
            self.subsidy_status = "Eligibility Checked"

    def check_eligibility(self):
        """Auto-check PMAY CLSS eligibility"""
        eligible = False
        if self.is_first_home and self.aadhaar:
            income_map = {
                "EWS (Up to Rs.3L)": 300000,
                "LIG (Rs.3L-6L)": 600000,
                "MIG-I (Rs.6L-12L)": 1200000,
                "MIG-II (Rs.12L-18L)": 1800000,
            }
            # All categories up to MIG-II are eligible for CLSS
            if self.income_category in income_map:
                eligible = True

        self.eligible_for_clss = 1 if eligible else 0

    def calculate_subsidy(self):
        """Calculate CLSS subsidy amount based on income category"""
        subsidy_slabs = {
            "EWS (Up to Rs.3L)": 266000,
            "LIG (Rs.3L-6L)": 266000,
            "MIG-I (Rs.6L-12L)": 235000,
            "MIG-II (Rs.12L-18L)": 235000,
        }

        if self.eligible_for_clss and self.income_category in subsidy_slabs:
            self.subsidy_amount = subsidy_slabs[self.income_category]
            self.principal_reduction = self.subsidy_amount
