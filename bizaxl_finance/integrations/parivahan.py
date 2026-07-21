"""Parivahan — RC Hypothecation Integration

Vehicle RC status verification and hypothecation registration via Parivahan/Vahan API.
Used for Vehicle Loan vertical.

API Docs: https://parivahan.gov.in/
Reference: MoRTH, NIC
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def verify_rc(registration_number):
    """Verify vehicle RC details
    
    Args:
        registration_number: Vehicle registration number (e.g. KA01AB1234)
        
    Returns:
        dict with RC details (owner, make, model, hypothecation status)
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.parivahan_api_key:
        return _live_verify_rc(settings, registration_number)
    
    return {
        "mode": "stub",
        "success": True,
        "data": {
            "registration_number": registration_number.upper(),
            "owner_name": "Demo Vehicle Owner",
            "maker_model": "Honda City ZX CVT",
            "maker": "HONDA",
            "model": "CITY",
            "variant": "ZX CVT",
            "fuel_type": "Petrol",
            "engine_no": "ENG1234567",
            "chassis_no": "CHS1234567890",
            "registration_date": "2022-01-15",
            "valid_upto": "2032-01-14",
            "insurance_expiry": "2025-01-14",
            "hypothecation_status": "Active",
            "hypothecated_to": "HDFC Bank Ltd",
            "mv_tax_paid_upto": "2025-03-31",
            "status": "Active",
        },
        "message": f"RC details for {registration_number} retrieved (stub)",
    }


def submit_hypothecation(registration_number, financier_name, financier_pan):
    """Submit hypothecation registration request to Vahan
    
    Args:
        registration_number: Vehicle registration number
        financier_name: Bank/NBFC name
        financier_pan: Financier PAN
        
    Returns:
        dict with application reference
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.parivahan_api_key:
        import requests
        try:
            response = requests.post(
                f"{settings.parivahan_endpoint}/hypothecation",
                json={
                    "registration_no": registration_number,
                    "financier_name": financier_name,
                    "financier_pan": financier_pan,
                },
                headers={"x-api-key": settings.get_password("parivahan_api_key")},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"Parivahan hypothecation failed: {e}", "Parivahan")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "application_ref": f"VAHAN_STUB_{today().replace('-', '')}",
        "status": "Submitted",
        "message": f"Hypothecation for {registration_number} submitted to RTO (stub)",
    }


def check_hypothecation_status(application_ref):
    """Check the status of a hypothecation application"""
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.parivahan_api_key:
        import requests
        try:
            response = requests.get(
                f"{settings.parivahan_endpoint}/status/{application_ref}",
                headers={"x-api-key": settings.get_password("parivahan_api_key")},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"Parivahan status check failed: {e}", "Parivahan")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "application_ref": application_ref,
        "status": "Endorsed",
        "rto_remarks": "Hypothecation endorsed on RC",
        "message": "Hypothecation status: Endorsed (stub)",
    }


def _live_verify_rc(settings, registration_number):
    """Live: Verify RC via Parivahan API"""
    import requests
    try:
        response = requests.get(
            f"{settings.parivahan_endpoint}/rc/{registration_number}",
            headers={"x-api-key": settings.get_password("parivahan_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"RC verification failed: {e}", "Parivahan")
        return {"error": str(e), "mode": "live"}
