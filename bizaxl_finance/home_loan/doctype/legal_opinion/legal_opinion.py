import frappe
from frappe.model.document import Document
from frappe.utils import today


class LegalOpinion(Document):
    def validate(self):
        self.set_defaults()
        self.validate_opinion_consistency()

    def before_submit(self):
        self.update_loan_application_status()

    def set_defaults(self):
        if not self.opinion_date:
            self.opinion_date = today()

    def validate_opinion_consistency(self):
        """Validate that the legal opinion fields are consistent"""
        if self.legal_opinion_status == "Unfavorable" and self.recommendation == "Approve":
            frappe.throw(
                "Legal opinion is 'Unfavorable' but recommendation is 'Approve'. "
                "These are inconsistent."
            )

    def update_loan_application_status(self):
        """Update linked Loan Application with legal opinion status"""
        if self.loan_application and self.legal_opinion_status:
            frappe.db.set_value(
                "Loan Application",
                self.loan_application,
                "remarks",
                f"Legal Opinion: {self.legal_opinion_status} - {self.legal_opinion_summary or 'No summary'}"
            )
            frappe.msgprint(
                f"Legal opinion updated for Loan Application {self.loan_application}",
                alert=True, indicator="green"
            )
