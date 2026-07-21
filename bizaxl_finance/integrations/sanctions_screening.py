"""Sanctions Screening Integration (OFAC / UN / PEP / FIU-IND)

Real-time AML screening at onboarding and per transaction.
Integrates with World-Check, OFAC SDN, UN Sanctions, and PEP lists.

Compliance: FIU-IND, PMLA 2002
Reference: https://www.fiuindia.gov.in/
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def screen_customer(customer_name, pan_number=None, aadhaar=None):
    """Screen a customer against all sanctions lists
    
    Args:
        customer_name: Full name to screen
        pan_number: Optional PAN for enhanced check
        aadhaar: Optional Aadhaar number
        
    Returns:
        dict with screening result, matches, and risk level
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.sanctions_api_key:
        return _live_screen(settings, customer_name, pan_number, aadhaar)
    return _stub_screen(customer_name, pan_number)


def check_pep_list(name, designation=None):
    """Check if a person is a Politically Exposed Person (PEP)
    
    Returns:
        dict with PEP status and details
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.sanctions_api_key:
        import requests
        try:
            response = requests.post(
                f"{settings.sanctions_endpoint}/pep",
                json={"name": name, "designation": designation or ""},
                headers={"x-api-key": settings.get_password("sanctions_api_key")},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"PEP check failed: {e}", "Sanctions")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "is_pep": False,
        "matches": [],
        "message": "PEP check completed — no matches (stub)",
    }


def check_watchlist(transaction_details):
    """Screen a transaction against sanctions watchlists"""
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.sanctions_api_key:
        import requests
        try:
            response = requests.post(
                f"{settings.sanctions_endpoint}/watchlist",
                json=transaction_details,
                headers={"x-api-key": settings.get_password("sanctions_api_key")},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"Watchlist screening failed: {e}", "Sanctions")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "risk_level": "Low",
        "matches_found": 0,
        "message": "Transaction watchlist screening passed (stub)",
    }


def _stub_screen(customer_name, pan_number=None):
    """Stub: Simulate sanctions screening"""
    import hashlib
    
    # Deterministic stub: generate harmless result
    risk = "Low"
    return {
        "mode": "stub",
        "success": True,
        "customer_name": customer_name,
        "risk_level": risk,
        "score": 12,
        "matches_found": 0,
        "matches": [],
        "lists_checked": ["OFAC SDN", "UN Sanctions", "EU Consolidated", "FIU-IND Watchlist"],
        "message": f"Screening completed — risk level: {risk} (stub)",
        "screened_on": str(now_datetime()),
    }


def _live_screen(settings, customer_name, pan_number=None, aadhaar=None):
    """Live: Screen customer via sanctions API"""
    import requests
    try:
        payload = {"name": customer_name}
        if pan_number:
            payload["pan"] = pan_number
        if aadhaar:
            payload["aadhaar"] = aadhaar
        
        response = requests.post(
            f"{settings.sanctions_endpoint}/screen",
            json=payload,
            headers={"x-api-key": settings.get_password("sanctions_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"Sanctions screening failed: {e}", "Sanctions")
        return {"error": str(e), "mode": "live"}
