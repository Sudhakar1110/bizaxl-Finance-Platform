"""e-Sign / DigiLocker Integration

e-Sign: Aadhaar-based digital signing of loan agreements
DigiLocker: Retrieve and verify digital documents

Spec:
    - e-Sign: https://www.cca.gov.in/esign/
    - DigiLocker: https://www.digilocker.gov.in/
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def generate_document(document_type, customer_data, agreement_data):
    """Generate a digital document for e-signing
    
    Args:
        document_type: Type of document (Loan Agreement, Sanction Letter, etc.)
        customer_data: Customer details for the document
        agreement_data: Terms and conditions
        
    Returns:
        dict with document_id and signing URL
    """
    # Document generation is local — no API key needed
    try:
        import json
        
        doc_id = f"DOC_{customer_data.get('name', 'UNKNOWN')}_{today()}"
        
        # In production: generate PDF using Frappe's Print Format engine
        # frappe.get_print(...) or custom template
        
        return {
            "mode": "stub",
            "success": True,
            "document_id": doc_id,
            "document_type": document_type,
            "generated_on": str(today()),
            "message": f"{document_type} generated (stub). Ready for e-sign.",
        }
    except Exception as e:
        frappe.log_error(f"Document generation failed: {e}", "e-Sign")
        return {"error": str(e)}


def request_esign(document_id, aadhaar_number, callback_url=None):
    """Request e-Sign on a document via Aadhaar OTP
    
    Args:
        document_id: Document to be signed
        aadhaar_number: Customer's Aadhaar for OTP
        callback_url: URL to receive signing callback
        
    Returns:
        dict with signing reference and status
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.esign_api_key:
        return _live_request_esign(settings, document_id, aadhaar_number, callback_url)
    
    return {
        "mode": "stub",
        "success": True,
        "signing_ref": f"ESIGN_STUB_{document_id}",
        "status": "Signed",
        "signed_document_url": f"https://stub.bizaxl.com/docs/{document_id}/signed",
        "message": "Document e-signed successfully via Aadhaar OTP (stub)",
        "timestamp": str(now_datetime()),
    }


def verify_esign(signing_ref):
    """Verify that an e-signed document is valid
    
    Returns:
        dict with verification status and certificate details
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.esign_api_key:
        import requests
        try:
            response = requests.get(
                f"{settings.esign_endpoint}/verify/{signing_ref}",
                headers={"x-api-key": settings.get_password("esign_api_key")},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"e-Sign verification failed: {e}", "e-Sign")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "signing_ref": signing_ref,
        "is_valid": True,
        "signed_by": "Aadhaar Holder",
        "signed_on": str(today()),
        "certificate": "ESIGN_CERT_STUB_1234",
        "message": "e-Signature verified (stub)",
    }


def fetch_digilocker_document(aadhaar_number, document_type="Aadhaar"):
    """Fetch document from DigiLocker
    
    Args:
        aadhaar_number: Customer Aadhaar
        document_type: Type of document to fetch (Aadhaar, PAN, etc.)
        
    Returns:
        dict with document data
    """
    # DigiLocker requires separate API key setup
    return {
        "mode": "stub",
        "success": True,
        "document_type": document_type,
        "document_data": "Base64 encoded document XML",
        "issuers": ["UIDAI"],
        "message": f"{document_type} retrieved from DigiLocker (stub)",
    }


def _live_request_esign(settings, document_id, aadhaar_number, callback_url=None):
    """Live: Request e-Sign via CCA API"""
    import requests
    try:
        payload = {
            "document_id": document_id,
            "aadhaar": aadhaar_number,
            "signing_type": "AadhaarOTP",
        }
        if callback_url:
            payload["callback_url"] = callback_url
        
        response = requests.post(
            f"{settings.esign_endpoint}/sign",
            json=payload,
            headers={"x-api-key": settings.get_password("esign_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"e-Sign request failed: {e}", "e-Sign")
        return {"error": str(e), "mode": "live"}
