import frappe
from frappe.model.document import Document


class ProvisioningRule(Document):
    """RBI-prescribed provisioning rules for NPA classification.
    
    Standard provisioning as per RBI Master Directions:
    - SMA-0: 0% (1-30 days)
    - SMA-1: 5% (31-60 days) 
    - SMA-2: 10% (61-90 days)
    - Sub-Standard: 15% (91-365 days)
    - Doubtful: 25-100% (1-3 years)
    - Loss: 100%
    """
    
    def validate(self):
        self.validate_days_range()
        self.validate_percentage()
    
    def validate_days_range(self):
        if self.days_past_due_min and self.days_past_due_max:
            if self.days_past_due_min > self.days_past_due_max:
                frappe.throw("Min days cannot exceed Max days")
    
    def validate_percentage(self):
        if self.provision_percentage < 0 or self.provision_percentage > 100:
            frappe.throw("Provision percentage must be between 0 and 100")
    
    @staticmethod
    def get_provision_rate(dpd_days):
        """Get provision percentage based on days past due per RBI norms"""
        rule = frappe.db.get_value(
            "Provisioning Rule",
            {
                "days_past_due_min": ["<=", dpd_days],
                "days_past_due_max": [">=", dpd_days],
                "is_active": 1,
            },
            "provision_percentage"
        )
        return rule or 0
    
    @staticmethod
    def get_default_rules():
        """Return standard RBI provisioning rules"""
        return [
            {"npa_category": "Standard", "min": 0, "max": 0, "provision": 0},
            {"npa_category": "SMA-0", "min": 1, "max": 30, "provision": 0},
            {"npa_category": "SMA-1", "min": 31, "max": 60, "provision": 5},
            {"npa_category": "SMA-2", "min": 61, "max": 90, "provision": 10},
            {"npa_category": "Sub-Standard", "min": 91, "max": 365, "provision": 15},
            {"npa_category": "Doubtful", "min": 366, "max": 1095, "provision": 25},
            {"npa_category": "Loss", "min": 1096, "max": 99999, "provision": 100},
        ]
