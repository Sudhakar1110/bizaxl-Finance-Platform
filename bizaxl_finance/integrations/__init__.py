"""Bizaxl Finance — Central Integration Registry

All 18 external API integrations follow the stub-to-live pattern:
- Stub mode: Works without API keys, returns realistic sample data
- Live mode: When credentials are configured in Integration Settings,
  automatically switches to real API calls
"""

import frappe

INTEGRATION_REGISTRY = {
    "uidai": {"label": "UIDAI Aadhaar eKYC", "module": "bizaxl_finance.integrations.uidai"},
    "pan_verify": {"label": "NSDL PAN Verification", "module": "bizaxl_finance.integrations.pan_verify"},
    "bureau": {"label": "Credit Bureau (CIBIL/Experian/CRIF/Equifax)", "module": "bizaxl_finance.integrations.bureau"},
    "account_aggregator": {"label": "Account Aggregator (Sahamati)", "module": "bizaxl_finance.integrations.account_aggregator"},
    "npci_payments": {"label": "NPCI — UPI/IMPS/NEFT/RTGS", "module": "bizaxl_finance.integrations.npci_payments"},
    "nach": {"label": "NACH / UPI AutoPay", "module": "bizaxl_finance.integrations.nach"},
    "notification_gateway": {"label": "SMS / WhatsApp / Email", "module": "bizaxl_finance.integrations.notification_gateway"},
    "video_kyc": {"label": "Video KYC", "module": "bizaxl_finance.integrations.video_kyc"},
    "sanctions_screening": {"label": "Sanctions — OFAC/UN/PEP", "module": "bizaxl_finance.integrations.sanctions_screening"},
    "esign": {"label": "e-Sign / DigiLocker", "module": "bizaxl_finance.integrations.esign"},
    "gstn": {"label": "GSTN API", "module": "bizaxl_finance.integrations.gstn"},
    "mcx_gold": {"label": "MCX — Live Gold Rate", "module": "bizaxl_finance.integrations.mcx_gold"},
    "treds": {"label": "TReDS Platform", "module": "bizaxl_finance.integrations.treds"},
    "parivahan": {"label": "Parivahan — RC Hypothecation", "module": "bizaxl_finance.integrations.parivahan"},
    "cersai": {"label": "CERSAI — Mortgage Registry", "module": "bizaxl_finance.integrations.cersai"},
    "csis": {"label": "CSIS — Education Subsidy", "module": "bizaxl_finance.integrations.csis"},
    "pmay": {"label": "PMAY / NHB", "module": "bizaxl_finance.integrations.pmay"},
    "scorecard": {"label": "AI/ML Scorecard Engine", "module": "bizaxl_finance.integrations.scorecard"},
}


def get_integration_settings():
    """Get the singleton Integration Settings document"""
    try:
        return frappe.get_single_doc("Integration Settings")
    except Exception:
        frappe.log_error("Failed to load Integration Settings", "Integrations")
        return frappe._dict()


def get_connector(name):
    """Get a connector module by registry name.
    
    Usage:
        connector = get_connector("mcx_gold")
        result = connector.get_live_gold_rate()
    """
    if name not in INTEGRATION_REGISTRY:
        raise ValueError(f"Unknown integration: {name}. Valid options: {list(INTEGRATION_REGISTRY.keys())}")
    
    import importlib
    info = INTEGRATION_REGISTRY[name]
    return importlib.import_module(info["module"])


def is_live_mode(name):
    """Check if an integration has API credentials configured (live mode)"""
    settings = get_integration_settings()
    if not settings:
        return False
    key_map = {
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
    field = key_map.get(name)
    if not field:
        return False
    return bool(getattr(settings, field, None))
