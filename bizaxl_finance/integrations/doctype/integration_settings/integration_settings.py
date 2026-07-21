import frappe
from frappe.model.document import Document


class IntegrationSettings(Document):
    """Central configuration for all 18 external API integrations.
    
    Each integration has its own section of credential fields.
    When credentials are entered, the integration switches from
    stub (simulated) mode to live (real API) mode automatically.
    """
    
    def validate(self):
        self.validate_endpoints()
    
    def validate_endpoints(self):
        """Basic URL validation for all configured endpoints"""
        endpoint_fields = [
            "uidai_endpoint", "pan_endpoint", "bureau_endpoint",
            "aa_endpoint", "esign_endpoint", "npci_api_endpoint",
            "nach_api_endpoint", "smsgateway_endpoint", "whatsapp_endpoint",
            "sanctions_endpoint", "gstn_endpoint", "mcx_endpoint",
            "treds_endpoint", "parivahan_endpoint", "cersai_endpoint",
            "scorecard_endpoint",
        ]
        for field in endpoint_fields:
            value = getattr(self, field, None)
            if value and not value.startswith(("http://", "https://")):
                frappe.msgprint(
                    f"Warning: {field} should start with http:// or https://",
                    alert=True
                )
    
    def is_integration_active(self, integration_key):
        """Check if a specific integration has credentials configured.
        
        Args:
            integration_key: One of 'uidai', 'pan_verify', 'bureau',
                           'account_aggregator', 'npci_payments', 'nach',
                           'notification_gateway', 'video_kyc',
                           'sanctions_screening', 'esign', 'gstn',
                           'mcx_gold', 'treds', 'parivahan', 'cersai',
                           'csis', 'pmay', 'scorecard'
        """
        key_field_map = {
            "uidai": "uidai_api_key",
            "pan_verify": "pan_api_key",
            "bureau": "bureau_api_key",
            "account_aggregator": "aa_client_id",
            "npci_payments": "npci_api_key",
            "nach": "nach_api_key",
            "notification_gateway": "smsgateway_api_key",
            "video_kyc": "video_kyc_api_key",
            "sanctions_screening": "sanctions_api_key",
            "esign": "esign_api_key",
            "gstn": "gstn_api_key",
            "mcx_gold": "mcx_api_key",
            "treds": "treds_api_key",
            "parivahan": "parivahan_api_key",
            "cersai": "cersai_api_key",
            "csis": "csis_api_key",
            "pmay": "pmay_api_key",
            "scorecard": "scorecard_model_path",
        }
        field = key_field_map.get(integration_key)
        if not field:
            return False
        return bool(getattr(self, field, None))
