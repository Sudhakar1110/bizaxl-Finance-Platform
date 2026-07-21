"""CERSAAI — Mortgage Registry Integration

Immovable property mortgage registration for Home Loans and MSME Secured Loans.
Charge creation, modification, and release via CERSAI portal.

Reference: https://www.cersai.org.in/
RBI: CERSAI registration mandatory for secured loans > Rs.5L
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def create_charge(property_details, loan_details, borrower_details):
    """Create a mortgage charge on CERSAI
    
    Args:
        property_details: Property address, area, value, title deed
        loan_details: Loan amount, sanction date, loan account
        borrower_details: Borrower name, PAN, Aadhaar
        
    Returns:
        dict with CERSAI reference and charge ID
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.cersai_api_key:
        return _live_create_charge(settings, property_details, loan_details, borrower_details)
    
    return {
        "mode": "stub",
        "success": True,
        "cersai_reference": f"CRS_STUB_{today().replace('-', '')}_{loan_details.get('account_no', 'NA')[-6:]}",
        "charge_id": f"CHG{today().replace('-', '')}001",
        "status": "Registered",
        "registration_date": str(today()),
        "message": "Mortgage charge registered on CERSAI (stub)",
    }


def verify_charge(charge_id, property_address):
    """Verify existing charge on a property
    
    Returns:
        dict with charge details and existing loans
    """
    # In production: query CERSAI to check if property is already charged
    return {
        "mode": "stub",
        "success": True,
        "charge_id": charge_id,
        "property_address": property_address,
        "existing_charges": [],
        "is_clear": True,
        "message": "Property has no existing charges — clear for new mortgage (stub)",
    }


def release_charge(charge_id, loan_account, release_reason="Loan Repaid"):
    """Release a mortgage charge after loan closure
    
    Args:
        charge_id: CERSAI charge ID to release
        loan_account: Loan account number
        release_reason: Reason for release
        
    Returns:
        dict with release confirmation
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.cersai_api_key:
        import requests
        try:
            response = requests.post(
                f"{settings.cersai_endpoint}/charge/release",
                json={
                    "charge_id": charge_id,
                    "loan_account": loan_account,
                    "reason": release_reason,
                },
                headers={"x-api-key": settings.get_password("cersai_api_key")},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"CERSAI charge release failed: {e}", "CERSAI")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "charge_id": charge_id,
        "release_date": str(today()),
        "status": "Released",
        "message": f"Mortgage charge {charge_id} released (stub)",
    }


def _live_create_charge(settings, property_details, loan_details, borrower_details):
    """Live: Create charge on CERSAI"""
    import requests
    try:
        response = requests.post(
            f"{settings.cersai_endpoint}/charge/create",
            json={
                "property": property_details,
                "loan": loan_details,
                "borrower": borrower_details,
            },
            headers={"x-api-key": settings.get_password("cersai_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"CERSAI charge creation failed: {e}", "CERSAI")
        return {"error": str(e), "mode": "live"}
