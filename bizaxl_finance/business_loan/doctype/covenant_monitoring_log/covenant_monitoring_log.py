import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months


class CovenantMonitoringLog(Document):
    def validate(self):
        self.auto_check_compliance()
        self.set_next_monitoring()

    def before_save(self):
        if not self.monitoring_date:
            self.monitoring_date = today()

    def auto_check_compliance(self):
        """Auto-check covenant compliance based on covenant type"""
        if not self.actual_value or not self.required_value:
            self.result = "Not Monitored"
            return

        # Define thresholds for different covenant types
        thresholds = {
            "DSCR": {"min": 1.25, "critical": 1.0},
            "Current Ratio": {"min": 1.33, "critical": 1.0},
            "Debt Equity Ratio": {"max": 3.0, "critical": 4.0},
            "Net Worth": {"min": 0, "critical": None},
            "Interest Coverage": {"min": 2.0, "critical": 1.0},
            "Fixed Asset Coverage": {"min": 1.25, "critical": 1.0},
            "Working Capital": {"min": 0, "critical": None},
        }

        threshold = thresholds.get(self.covenant_type)
        if not threshold:
            self.result = "Not Monitored"
            return

        if "min" in threshold and threshold["min"] is not None:
            if threshold["critical"] is not None and self.actual_value < threshold["critical"]:
                self.result = "Critical"
            elif self.actual_value < threshold["min"]:
                self.result = "Breached"
            else:
                self.result = "Compliant"
        elif "max" in threshold and threshold["max"] is not None:
            if threshold["critical"] is not None and self.actual_value > threshold["critical"]:
                self.result = "Critical"
            elif self.actual_value > threshold["max"]:
                self.result = "Breached"
            else:
                self.result = "Compliant"

        # Trigger alert on breach
        if self.result in ("Breached", "Critical"):
            self._send_breach_alert()

    def set_next_monitoring(self):
        """Set next monitoring date based on frequency (stored in remarks field)"""
        next_date = today()
        if self.result == "Critical":
            next_date = add_months(today(), 1)
        elif self.result == "Breached":
            next_date = add_months(today(), 3)
        else:
            next_date = add_months(today(), 6)

        # Store next monitoring info in remarks
        self.remarks = f"Next review: {next_date}. Last check: {today()}. Result: {self.result}" if not self.remarks else self.remarks

    def _send_breach_alert(self):
        """Send notification on covenant breach"""
        breach_type = "CRITICAL" if self.result == "Critical" else "BREACH"
        try:
            frappe.get_doc({
                "doctype": "Customer Communication",
                "customer": self.name,
                "subject": f"Covenant {breach_type}: {self.covenant_type}",
                "message_body": (
                    f"Covenant {self.covenant_type}: Required "
                    f"{self.required_value}, Actual {self.actual_value}. "
                    f"Result: {self.result}"
                ),
                "channel": "App Notification",
                "communication_type": "Alert",
                "status": "Draft",
                "reference_doctype": "Covenant Monitoring Log",
                "reference_name": self.name,
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to send covenant breach alert: {e}", "Covenant Monitor")
