import frappe
from frappe.model.document import Document
from frappe.utils import today


class PropertyDetail(Document):
    def validate(self):
        self.validate_legal_status()
        self.calculate_ltv()
        self.validate_construction_stage()

    def before_save(self):
        if not self.legal_status:
            self.legal_status = "Pending Verification"

    def validate_legal_status(self):
        """Track legal due diligence status"""
        if self.title_deed_number and not self.legal_status:
            self.legal_status = "Pending Verification"
        if self.encumbrance_certificate and self.legal_status == "Pending Verification":
            self.legal_status = "Clear Title"

    def calculate_ltv(self):
        """Auto-calculate Loan-to-Value based on valuation"""
        if self.valuated_amount and self.agreed_value:
            ltv = round((self.agreed_value / self.valuated_amount) * 100, 2) if self.valuated_amount else 0
            # For Home Loans, max LTV is typically 80-90%
            if ltv > 90:
                frappe.msgprint(f"Warning: LTV ratio {ltv}% exceeds recommended 90% limit")

    def validate_construction_stage(self):
        """Validate construction stage for under-construction properties"""
        if self.property_type == "Under Construction" and not self.construction_stage:
            frappe.throw("Construction Stage is required for Under Construction properties")

    def get_legal_documents_status(self):
        """Return status of legal document verification"""
        docs_status = {
            "title_deed": bool(self.title_deed_number),
            "encumbrance": bool(self.encumbrance_certificate),
            "legal_opinion": self.legal_status == "Clear Title",
        }
        return docs_status

    def get_engineer_certificate_required(self):
        """Check if engineer certificate is needed for stage verification"""
        if self.property_type == "Under Construction" and self.construction_stage:
            return True
        return False
