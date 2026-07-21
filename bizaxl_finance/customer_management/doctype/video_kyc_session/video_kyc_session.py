import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class VideoKYCSession(Document):
    def validate(self):
        self.validate_dates()
        self.set_defaults()

    def validate_dates(self):
        if self.session_expiry and not self.get("__islocal"):
            if now_datetime() > self.session_expiry and self.session_status == "Scheduled":
                self.session_status = "Expired"

    def set_defaults(self):
        if not self.session_status:
            self.session_status = "Scheduled"

    def before_insert(self):
        """Auto-create session via video KYC integration"""
        self.create_external_session()

    def create_external_session(self):
        """Create session via the video KYC integration service"""
        from bizaxl_finance.integrations.video_kyc import create_session as create_vkyc_session

        customer_name = frappe.db.get_value("Bizaxl Customer", self.customer, "customer_name")
        result = create_vkyc_session(customer_name, self.agent_name)

        if result.get("success") or result.get("mode") == "stub":
            self.session_id = result.get("session_id")
            self.session_url = result.get("session_url")
            if result.get("expires_at"):
                from frappe.utils import get_datetime
                self.session_expiry = get_datetime(result["expires_at"])
        else:
            frappe.log_error(
                f"Video KYC session creation failed for {self.customer}: {result}",
                "Video KYC"
            )

    def complete_session(self):
        """Mark session as completed"""
        self.session_status = "Completed"
        self.save(ignore_permissions=True)

    def verify_session(self, status="Approved", verified_by=None, notes=None):
        """Verify the KYC session"""
        from bizaxl_finance.integrations.video_kyc import verify_session as verify_vkyc

        if self.session_id:
            verify_vkyc(self.session_id)

        self.verification_status = status
        self.verified_by = verified_by or frappe.session.user
        self.verified_on = now_datetime()
        if notes:
            self.agent_notes = notes
        self.save(ignore_permissions=True)
