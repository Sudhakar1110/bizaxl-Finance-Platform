import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ColendingPartnership(Document):
    def validate(self):
        self.validate_shares()
        self.validate_partner_share()

    def validate_shares(self):
        """Validate that participation shares sum correctly"""
        total = flt(self.lead_participation_percent) + flt(self.partner_participation_percent)
        if abs(total - 100) > 0.01:
            frappe.throw(
                f"Lead ({self.lead_participation_percent}%) + Partner "
                f"({self.partner_participation_percent}%) participation "
                f"must equal 100% (currently {total}%)"
            )

    def validate_partner_share(self):
        if self.risk_share_lead_percent + self.risk_share_partner_percent != 100:
            frappe.msgprint(
                f"Risk shares total {self.risk_share_lead_percent + self.risk_share_partner_percent}%, expected 100%",
                indicator="orange"
            )

    def calculate_split(self, loan_amount, interest_amount, processing_fee=0):
        """Calculate P&L split for a given loan"""
        return {
            "lead": {
                "principal_share": flt(loan_amount * self.lead_participation_percent / 100),
                "interest_share": flt(interest_amount * self.lead_participation_percent / 100),
                "processing_fee_share": flt(processing_fee * self.lead_processing_fee_share / 100),
                "risk_share": self.risk_share_lead_percent,
            },
            "partner": {
                "principal_share": flt(loan_amount * self.partner_participation_percent / 100),
                "interest_share": flt(interest_amount * self.partner_participation_percent / 100),
                "processing_fee_share": flt(processing_fee * self.partner_processing_fee_share / 100),
                "risk_share": self.risk_share_partner_percent,
            },
            "partner_name": self.partner_entity,
            "partnership": self.name,
        }

    def update_portfolio_summary(self):
        """Refresh portfolio summary from linked loans"""
        loan_apps = frappe.get_all("Loan Application",
            filters={"custom_colending_partnership": self.name},
            fields=["loan_amount", "name"]
        )

        self.total_loans_funded = len(loan_apps)
        self.total_disbursed_amount = sum(
            flt(frappe.db.get_value("Loan Disbursement",
                {"loan_application": la.name}, "disbursed_amount") or 0)
            for la in loan_apps
        )
        self.save(ignore_permissions=True)
