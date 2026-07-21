"""NPCI Payment Rail Integration (UPI / IMPS / NEFT / RTGS)

Handles all payment execution: disbursement, collection, and bulk payments.
Stub-to-live pattern as per NPCI API specifications.

Payment rails:
    - UPI: Real-time, 24x7, up to Rs.5L per transaction
    - IMPS: Real-time, 24x7, up to Rs.5L
    - NEFT: Batch process, 30-min slots, no limit
    - RTGS: Real-time, Rs.2L minimum, no upper limit
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def initiate_upi_transfer(upi_id, amount, merchant_ref, description=""):
    """Initiate a UPI payment transfer
    
    Args:
        upi_id: Beneficiary UPI ID (e.g. name@bank)
        amount: Amount in INR
        merchant_ref: Merchant transaction reference
        description: Payment description
        
    Returns:
        dict with transaction status
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.npci_api_key:
        return _live_initiate(settings, "UPI", upi_id, amount, merchant_ref, description)
    return _stub_initiate("UPI", upi_id, amount, merchant_ref)


def initiate_neft(beneficiary_account, beneficiary_ifsc, amount, merchant_ref):
    """Initiate NEFT transfer"""
    settings = frappe.get_single_doc("Integration Settings")
    if settings.npci_api_key:
        return _live_initiate(settings, "NEFT", beneficiary_account, amount, merchant_ref, "")
    return _stub_initiate("NEFT", beneficiary_account, amount, merchant_ref)


def initiate_imps(beneficiary_mobile, amount, merchant_ref):
    """Initiate IMPS transfer to mobile number"""
    settings = frappe.get_single_doc("Integration Settings")
    if settings.npci_api_key:
        return _live_initiate(settings, "IMPS", beneficiary_mobile, amount, merchant_ref, "")
    return _stub_initiate("IMPS", beneficiary_mobile, amount, merchant_ref)


def initiate_rtgs(beneficiary_account, beneficiary_ifsc, amount, merchant_ref):
    """Initiate RTGS transfer (min Rs.2L)"""
    if amount < 200000:
        return {"error": "RTGS minimum amount is Rs.2,00,000", "mode": "stub"}
    
    settings = frappe.get_single_doc("Integration Settings")
    if settings.npci_api_key:
        return _live_initiate(settings, "RTGS", beneficiary_account, amount, merchant_ref, "")
    return _stub_initiate("RTGS", beneficiary_account, amount, merchant_ref)


def check_transaction_status(provider_reference):
    """Check status of a previously initiated transaction"""
    settings = frappe.get_single_doc("Integration Settings")
    if settings.npci_api_key:
        import requests
        try:
            response = requests.get(
                f"{settings.npci_api_endpoint}/status/{provider_reference}",
                headers={
                    "x-api-key": settings.get_password("npci_api_key"),
                    "merchant-id": settings.npci_merchant_id,
                },
                timeout=15,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"NPCI status check failed: {e}", "NPCI")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "status": "Completed",
        "provider_reference": provider_reference,
        "message": "Transaction status: Completed (stub)",
    }


def _stub_initiate(payment_type, beneficiary, amount, merchant_ref):
    """Stub: Simulate payment initiation"""
    return {
        "mode": "stub",
        "success": True,
        "payment_type": payment_type,
        "amount": amount,
        "provider_reference": f"STUB_{payment_type}_{now_datetime().strftime('%Y%m%d%H%M%S')}",
        "status": "Completed",
        "message": f"{payment_type} of ₹{amount:,.2f} initiated successfully (stub)",
        "timestamp": str(now_datetime()),
    }


def _live_initiate(settings, payment_type, beneficiary, amount, merchant_ref, description):
    """Live: Initiate payment via NPCI API"""
    import requests
    try:
        payload = {
            "payment_type": payment_type,
            "beneficiary": beneficiary,
            "amount": amount,
            "merchant_ref": merchant_ref,
            "description": description,
        }
        if payment_type == "NEFT":
            payload["beneficiary_account"] = beneficiary
            payload["beneficiary_ifsc"] = merchant_ref
        
        response = requests.post(
            f"{settings.npci_api_endpoint}/pay",
            json=payload,
            headers={
                "x-api-key": settings.get_password("npci_api_key"),
                "merchant-id": settings.npci_merchant_id,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"NPCI payment failed ({payment_type}): {e}", "NPCI")
        return {"error": str(e), "mode": "live"}
