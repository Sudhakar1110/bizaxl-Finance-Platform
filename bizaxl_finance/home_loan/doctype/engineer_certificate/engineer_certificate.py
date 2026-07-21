import frappe
from frappe.model.document import Document
from frappe.utils import today


class EngineerCertificate(Document):
    def validate(self):
        self.set_defaults()
        self.validate_stage_consistency()

    def before_submit(self):
        self.certify_stage()
        self.update_tranche_disbursement()

    def set_defaults(self):
        if not self.inspection_date:
            self.inspection_date = today()
        if not self.percentage_complete and self.current_stage == "Completed":
            self.percentage_complete = 100

    def validate_stage_consistency(self):
        """Validate that current stage and certified stage make sense"""
        stages = [
            "Not Started", "Site Preparation", "Foundation", "Ground Floor",
            "First Floor", "Second Floor", "Roof", "External Finishing",
            "Internal Finishing", "Completed"
        ]

        if self.current_stage and self.certified_stage:
            current_idx = stages.index(self.current_stage) if self.current_stage in stages else 0
            certified_idx = stages.index(self.certified_stage) if self.certified_stage in stages else 0

            if certified_idx > current_idx:
                frappe.throw(
                    f"Cannot certify stage '{self.certified_stage}' when current "
                    f"construction stage is '{self.current_stage}'"
                )

    def certify_stage(self):
        """Mark stage as certified and set validity"""
        if self.certification_status == "Certified":
            from frappe.utils import add_months
            self.valid_until = add_months(today(), 3)  # Certificate valid for 3 months

    def update_tranche_disbursement(self):
        """Auto-update linked Tranche Disbursement record"""
        if not self.stage_certified or not self.loan_application:
            return

        # Find matching tranche disbursement for this stage
        stage_map = {
            "Foundation": "Foundation",
            "Ground Floor": "Construction Stage 1",
            "First Floor": "Construction Stage 2",
            "Second Floor": "Construction Stage 2",
            "Roof": "Construction Stage 2",
            "External Finishing": "Finishing",
            "Internal Finishing": "Finishing",
            "Completed": "Finishing",
        }

        tranche_purpose = stage_map.get(self.certified_stage)
        if not tranche_purpose:
            return

        tranches = frappe.get_all(
            "Tranche Disbursement",
            filters={
                "loan_application": self.loan_application,
                "tranche_purpose": tranche_purpose,
                "status": ["in", ["Planned", "Approved"]]
            },
            limit=1
        )

        if tranches:
            tranche = frappe.get_doc("Tranche Disbursement", tranches[0].name)
            tranche.status = "Approved"
            if self.recommended_tranche_amount:
                tranche.tranche_amount = self.recommended_tranche_amount
            tranche.engineer_certificate_obtained = 1
            tranche.save(ignore_permissions=True)
            frappe.msgprint(
                f"Tranche Disbursement {tranche.name} approved via engineer certificate",
                alert=True, indicator="green"
            )
