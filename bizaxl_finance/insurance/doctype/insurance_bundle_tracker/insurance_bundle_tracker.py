import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days

class InsuranceBundleTracker(Document):
    def validate(self):
        self.validate_dates()

    def validate_dates(self):
        if self.policy_start_date and self.policy_end_date:
            if self.policy_end_date <= self.policy_start_date:
                frappe.throw("Policy end date must be after start date")

    def check_renewal_alert(self):
        """Check if renewal alert needs to be sent (called by scheduler)"""
        if not self.policy_end_date or not self.renewal_eligible:
            return

        alert_date = add_days(self.policy_end_date, -(self.renewal_alert_days_before or 30))

        if today() >= str(alert_date) and self.renewal_status == "Not Due":
            self.renewal_status = "Alert Sent"
            self.last_renewal_alert_date = today()
            self.save(ignore_permissions=True)
            return True

        return False

    def on_renewal(self, new_policy_number, renewal_date=None):
        """Handle policy renewal"""
        self.renewal_status = "Renewed"
        self.renewal_date = renewal_date or today()
        self.new_policy_number = new_policy_number
        self.status = "Renewed"
        self.save(ignore_permissions=True)
