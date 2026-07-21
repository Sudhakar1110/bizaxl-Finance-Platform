"""NSDL PAN Verification Integration

Stub-to-live pattern:
    Stub: Returns realistic PAN data without real API
    Live: Integrates with NSDL's PAN verification API

API Docs: https://nsdl.co.in/pan-services/
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def verify_pan(pan_number, name=None, dob=None):
    """Verify PAN card details.
    
    Args:
        pan_number: 10-character PAN
        name: Optional name to match against PAN holder name
        dob: Optional DOB to validate
        
    Returns:
        dict with verification result
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.pan_api_key:
        return _live_verify(settings, pan_number, name, dob)
    return _stub_verify(pan_number, name, dob)


def get_ckyc_number(pan_number):
    """Retrieve CKYC number for a given PAN"""
    # In production: call NSDL CKYC API
    return {
        "mode": "stub",
        "success": True,
        "ckyc_number": "CKYC1234567890",
        "message": "CKYC number retrieved (stub)",
    }


def _stub_verify(pan_number, name=None, dob=None):
    """Stub: Simulate PAN verification"""
    if not pan_number or len(pan_number) != 10:
        return {"error": "Invalid PAN format", "mode": "stub"}
    
    stub_data = {
        "pan": pan_number.upper(),
        "is_valid": True,
        "holder_name": (name or "Demo PAN Holder").title(),
        "pan_status": "Active",
        "pan_type": "Individual",
        "date_of_birth": dob or "1990-01-01",
        "aadhaar_linked": True,
    }
    
    # If name provided, simulate match check
    if name:
        stub_data["name_match"] = name.lower() == "demo pan holder"
    
    return {
        "mode": "stub",
        "success": True,
        "data": stub_data,
        "message": "PAN verified (stub)",
        "timestamp": str(now_datetime()),
    }


def _live_verify(settings, pan_number, name=None, dob=None):
    """Live: Verify PAN via NSDL API"""
    import requests
    try:
        payload = {"pan": pan_number.upper()}
        if name:
            payload["name"] = name
        if dob:
            payload["dob"] = dob
        
        response = requests.post(
            settings.pan_endpoint,
            json=payload,
            headers={"x-api-key": settings.get_password("pan_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"PAN verification failed: {e}", "PAN Verify")
        return {"error": str(e), "mode": "live"}
