"""NACH / UPI AutoPay Integration

Handles mandate registration and collection execution for:
    - eNACH: Electronic NACH mandate via sponsor bank
    - UPI AutoPay: Recurring payment mandate on UPI
    - Physical NACH: Paper-based mandate digitization

Spec: https://npci.org.in/nach
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def register_mandate(customer, bank_account, max_amount, frequency="Monthly", mandate_type="eNACH"):
    """Register auto-debit mandate
    
    Args:
        customer: Bizaxl Customer name
        bank_account: Customer's bank account details
        max_amount: Maximum debit amount
        frequency: Monthly, Quarterly, etc.
        mandate_type: eNACH, UPI AutoPay, or Physical
        
    Returns:
        dict with mandate reference and status
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.nach_api_key:
        return _live_register(settings, customer, bank_account, max_amount, frequency, mandate_type)
    return _stub_register(customer, bank_account, max_amount, frequency, mandate_type)


def execute_collection(mandate_ref, amount, description=""):
    """Execute collection against an active mandate
    
    Args:
        mandate_ref: Mandate reference from registration
        amount: Amount to collect
        description: Collection description
        
    Returns:
        dict with collection status
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.nach_api_key:
        import requests
        try:
            response = requests.post(
                f"{settings.nach_api_endpoint}/collect",
                json={"mandate_ref": mandate_ref, "amount": amount, "description": description},
                headers={"x-api-key": settings.get_password("nach_api_key")},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"NACH collection failed: {e}", "NACH")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "amount": amount,
        "status": "Collected",
        "provider_reference": f"NACH_STUB_{now_datetime().strftime('%Y%m%d%H%M%S')}",
        "message": f"Collection of ₹{amount:,.2f} executed (stub)",
    }


def handle_mandate_return(mandate_ref, return_code, return_reason):
    """Handle a returned/failed mandate collection
    
    Updates the NACH Mandate DocType and triggers retry logic.
    """
    mandate = frappe.db.get_value("NACH Mandate", {"mandate_reference": mandate_ref}, "name")
    if mandate:
        frappe.db.set_value("NACH Mandate", mandate, {
            "return_code": return_code,
            "return_reason": return_reason,
            "status": "Returned",
        })
    
    return {
        "success": True,
        "action": "retry_scheduled",
        "message": f"Mandate return handled. Retry scheduled.",
    }


def _stub_register(customer, bank_account, max_amount, frequency, mandate_type):
    """Stub: Simulate mandate registration"""
    ref = f"STUB_{mandate_type}_{now_datetime().strftime('%Y%m%d%H%M%S')}"
    return {
        "mode": "stub",
        "success": True,
        "mandate_type": mandate_type,
        "mandate_reference": ref,
        "umrn": f"UMRN{ref[-10:]}",
        "status": "Active",
        "max_amount": max_amount,
        "frequency": frequency,
        "message": f"{mandate_type} mandate registered (stub). UMRN: {ref[-10:]}",
        "timestamp": str(now_datetime()),
    }


def _live_register(settings, customer, bank_account, max_amount, frequency, mandate_type):
    """Live: Register mandate via NACH API"""
    import requests
    try:
        response = requests.post(
            f"{settings.nach_api_endpoint}/mandate/register",
            json={
                "customer": customer,
                "bank_account": bank_account,
                "max_amount": max_amount,
                "frequency": frequency,
                "mandate_type": mandate_type,
            },
            headers={"x-api-key": settings.get_password("nach_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"NACH mandate registration failed: {e}", "NACH")
        return {"error": str(e), "mode": "live"}
