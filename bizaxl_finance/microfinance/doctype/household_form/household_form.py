import frappe
from frappe.model.document import Document
from frappe.utils import flt

class HouseholdForm(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_assessment()

    def before_save(self):
        self.update_member_household_data()

    def calculate_totals(self):
        """Calculate total income, expenses, surplus, assets, and obligations"""
        # Total income
        self.total_monthly_income = flt(self.monthly_income) + \
            flt(self.spouse_income) + flt(self.other_household_income)

        # Total expenses
        self.total_monthly_expenses = flt(self.monthly_food_expenses) + \
            flt(self.monthly_rent) + flt(self.monthly_utilities) + \
            flt(self.monthly_transport) + flt(self.monthly_education) + \
            flt(self.monthly_healthcare) + flt(self.monthly_other_expenses)

        # Monthly surplus
        self.monthly_surplus = flt(self.total_monthly_income) - flt(self.total_monthly_expenses)

        # Total assets
        self.total_asset_value = flt(self.land_value) + flt(self.house_value) + \
            flt(self.vehicle_value) + flt(self.livestock_value) + \
            flt(self.other_assets_value)

        # Total obligations
        self.total_existing_obligations = flt(self.existing_loan_1_amount) + \
            flt(self.existing_loan_2_amount)

        # Monthly obligation payment (estimated)
        if self.total_existing_obligations > 0:
            self.monthly_obligation_payment = flt(self.total_existing_obligations * 0.03)

    def validate_assessment(self):
        """Validate assessment data"""
        if self.total_monthly_income and self.total_monthly_income <= 0:
            frappe.throw("Total monthly income must be greater than zero")

        if self.household_size and self.dependents_count:
            if self.dependents_count >= self.household_size:
                frappe.msgprint(
                    "Dependents count should be less than household size",
                    indicator="orange"
                )

    def update_member_household_data(self):
        """Update MFI Member with consolidated household data"""
        if self.member:
            member = frappe.get_doc("MFI Member", self.member)
            member.monthly_household_income = self.total_monthly_income
            member.total_existing_obligations = self.total_existing_obligations
            member.save(ignore_permissions=True)

    def get_assessment_summary(self):
        """Return a summary dict for credit decisioning"""
        return {
            "member": self.member,
            "member_name": self.member_name,
            "total_monthly_income": self.total_monthly_income,
            "total_monthly_expenses": self.total_monthly_expenses,
            "monthly_surplus": self.monthly_surplus,
            "total_asset_value": self.total_asset_value,
            "total_existing_obligations": self.total_existing_obligations,
            "monthly_obligation_payment": self.monthly_obligation_payment,
            "repayment_capacity": flt(self.monthly_surplus) - flt(self.monthly_obligation_payment),
            "bureau_score": self.bureau_score,
            "rs_2l_cap_compliant": self.rs_2l_cap_compliant,
            "multi_lender_count": self.multi_lender_count,
        }
