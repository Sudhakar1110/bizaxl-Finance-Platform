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
        """Update linked Loan Application with legal opinion status (appends to existing remarks)"""
        if self.loan_application and self.legal_opinion_status:
            existing_remarks = frappe.db.get_value(
                "Loan Application", self.loan_application, "remarks"
            ) or ""
            new_remark = (
                f"Legal Opinion: {self.legal_opinion_status}"
                f" - {self.legal_opinion_summary or 'No summary'}"
            )
            if existing_remarks:
                if new_remark not in existing_remarks:
                    updated_remarks = f"{existing_remarks}\n{new_remark}"
                else:
                    updated_remarks = existing_remarks
            else:
                updated_remarks = new_remark

            frappe.db.set_value(
                "Loan Application", self.loan_application, "remarks", updated_remarks
            )
            frappe.msgprint(
                f"Legal opinion updated for Loan Application {self.loan_application}",
                alert=True, indicator="green"
            )
