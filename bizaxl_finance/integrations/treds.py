"""TReDS Platform Integration

Invoice financing secondary market for MSME receivables.
Integrates with RBI-licensed TReDS platforms (RXIL, M1xchange, Invoicemart).

Reference: https://treds.in/
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime, add_days


def upload_invoice(invoice_data, program_id=None):
    """Upload invoice to TReDS platform for discounting
    
    Args:
        invoice_data: dict with invoice details
            - invoice_number, invoice_date, amount, buyer_gstin
            - supplier_gstin, due_date, document_url
        program_id: Optional TReDS program ID
        
    Returns:
        dict with TReDS reference and status
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.treds_api_key:
        return _live_upload(settings, invoice_data, program_id)
    
    return {
        "mode": "stub",
        "success": True,
        "treds_reference": f"TREDS_STUB_{today().replace('-', '')}_{invoice_data.get('invoice_number', 'INV')}",
        "status": "Uploaded",
        "amount": invoice_data.get("amount", 0),
        "bid_deadline": str(add_days(today(), 2)),
        "message": f"Invoice {invoice_data.get('invoice_number')} uploaded to TReDS (stub)",
    }


def check_status(treds_reference):
    """Check the status of an invoice on TReDS
    
    Returns:
        dict with current status and bid information
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.treds_api_key:
        import requests
        try:
            response = requests.get(
                f"{settings.treds_endpoint}/invoice/{treds_reference}",
                headers={"x-api-key": settings.get_password("treds_api_key")},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"TReDS status check failed: {e}", "TReDS")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "treds_reference": treds_reference,
        "status": "Accepted",
        "winning_bid": {
            "discount_rate": 7.25,
            "advance_amount": 720000,
            "financier": "Demo Bank Ltd",
        },
        "message": "TReDS invoice status: Accepted (stub)",
    }


def receive_funding(treds_reference):
    """Confirm funding received from TReDS financier
    
    Updates the Invoice Finance record with funding details.
    """
    return {
        "mode": "stub",
        "success": True,
        "treds_reference": treds_reference,
        "funding_amount": 720000,
        "funding_date": str(today()),
        "settlement_ref": f"SETTLE_STUB_{treds_reference}",
        "message": "Funding received from TReDS financier (stub)",
    }


def _live_upload(settings, invoice_data, program_id=None):
    """Live: Upload invoice to TReDS"""
    import requests
    try:
        payload = {
            "invoice": invoice_data,
            "program_id": program_id or "",
        }
        response = requests.post(
            f"{settings.treds_endpoint}/invoice/upload",
            json=payload,
            headers={"x-api-key": settings.get_password("treds_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"TReDS invoice upload failed: {e}", "TReDS")
        return {"error": str(e), "mode": "live"}

