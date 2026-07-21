"""UIDAI Aadhaar eKYC Integration

Stub-to-live pattern:
    Stub: Returns realistic Aadhaar data without real API
    Live: Integrates with UIDAI's eKYC API for OTP-based verification

API Docs: https://uidai.gov.in/ekyc.html
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime
import json


def verify_aadhaar_otp(aadhaar_number):
    """Step 1: Send OTP to Aadhaar number
    
    Args:
        aadhaar_number: 12-digit Aadhaar number
        
    Returns:
        dict with 'txn_id' (for step 2) and 'mode' ('live' or 'stub')
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.uidai_api_key:
        return _live_send_otp(settings, aadhaar_number)
    return _stub_send_otp(aadhaar_number)


def submit_ekyc(txn_id, otp, share_code=None):
    """Step 2: Submit OTP to fetch eKYC data
    
    Args:
        txn_id: Transaction ID from verify_aadhaar_otp()
        otp: 6-digit OTP received by customer
        share_code: Optional 4-digit code to encrypt XML
        
    Returns:
        dict with KYC data (name, DOB, address, photo, etc.)
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.uidai_api_key:
        return _live_submit_otp(settings, txn_id, otp, share_code)
    return _stub_submit_otp(txn_id, otp, share_code)


def _stub_send_otp(aadhaar_number):
    """Stub: Simulate sending OTP"""
    # Validate format
    if not aadhaar_number or len(aadhaar_number) != 12:
        return {"error": "Invalid Aadhaar number", "mode": "stub"}
    
    return {
        "mode": "stub",
        "success": True,
        "txn_id": f"STUB_TXN_{now_datetime().strftime('%Y%m%d%H%M%S')}",
        "message": f"OTP sent to Aadhaar ending {aadhaar_number[-4:]} (stub)",
        "timestamp": str(now_datetime()),
    }


def _stub_submit_otp(txn_id, otp, share_code=None):
    """Stub: Simulate eKYC response with realistic test data"""
    return {
        "mode": "stub",
        "success": True,
        "data": {
            "name": "Demo Customer",
            "dob": "1990-01-15",
            "gender": "Male",
            "phone": "9876543210",
            "email": "demo@example.com",
            "address": {
                "line1": "123, Test Layout",
                "line2": "Sector 5",
                "city": "Bangalore",
                "state": "Karnataka",
                "pincode": "560001",
            },
            "photo": "base64_encoded_photo_string",
            "is_verified": True,
        },
        "message": "eKYC verified successfully (stub)",
        "timestamp": str(now_datetime()),
    }


def _live_send_otp(settings, aadhaar_number):
    """Live: Send OTP via UIDAI API"""
    import requests
    try:
        response = requests.post(
            f"{settings.uidai_endpoint}/otp",
            json={"aadhaar": aadhaar_number, "channel": "SMS"},
            headers={
                "x-api-key": settings.get_password("uidai_api_key"),
                "Authorization": f"Bearer {settings.uidai_auth_token}",
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"UIDAI OTP failed: {e}", "UIDAI")
        return {"error": str(e), "mode": "live"}


def _live_submit_otp(settings, txn_id, otp, share_code=None):
    """Live: Submit OTP and fetch eKYC data"""
    import requests
    try:
        payload = {"txn_id": txn_id, "otp": otp}
        if share_code:
            payload["share_code"] = share_code
        
        response = requests.post(
            f"{settings.uidai_endpoint}/ekyc",
            json=payload,
            headers={
                "x-api-key": settings.get_password("uidai_api_key"),
                "Authorization": f"Bearer {settings.uidai_auth_token}",
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"UIDAI eKYC failed: {e}", "UIDAI")
        return {"error": str(e), "mode": "live"}


def validate_kyc_data(kyc_data):
    """Validate and normalize KYC data before saving"""
    if not kyc_data or not kyc_data.get("success"):
        return None
    
    data = kyc_data.get("data", {})
    return {
        "full_name": data.get("name", "").title(),
        "date_of_birth": data.get("dob"),
        "gender": data.get("gender"),
        "phone": data.get("phone"),
        "email": data.get("email"),
        "address": ", ".join(filter(None, [
            data.get("address", {}).get("line1", ""),
            data.get("address", {}).get("line2", ""),
            data.get("address", {}).get("city", ""),
            data.get("address", {}).get("state", ""),
            data.get("address", {}).get("pincode", ""),
        ])),
        "kyc_verified_on": str(today()),
    }
