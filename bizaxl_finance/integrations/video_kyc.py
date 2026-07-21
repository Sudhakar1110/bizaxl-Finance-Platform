"""Video KYC Integration

Handles in-app video KYC sessions with agent queue, session recording,
and KYC vault upload. Supports RBI-compliant Video KYC process.

Regulatory ref: RBI Master Direction on KYC (Updated 2023)
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def create_session(customer_name, agent_name=None):
    """Create a Video KYC session
    
    Args:
        customer_name: Customer name for the session
        agent_name: Optional assign specific agent
        
    Returns:
        dict with session URL and details
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.video_kyc_api_key:
        return _live_create_session(settings, customer_name, agent_name)
    
    import uuid
    session_id = f"VKYC_{uuid.uuid4().hex[:12].upper()}"
    return {
        "mode": "stub",
        "success": True,
        "session_id": session_id,
        "session_url": f"https://vkyc-stub.bizaxl.com/session/{session_id}",
        "agent_name": agent_name or "Demo Agent",
        "expires_at": str(now_datetime()),
        "message": f"Video KYC session created for {customer_name} (stub)",
    }


def upload_recording(session_id, recording_data, recording_type="video/mp4"):
    """Upload Video KYC session recording to secure vault"""
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.video_kyc_api_key:
        import requests
        try:
            response = requests.post(
                f"{settings.video_kyc_api_key}/upload",
                files={"recording": (f"{session_id}.mp4", recording_data, recording_type)},
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            frappe.log_error(f"Video KYC upload failed: {e}", "Video KYC")
            return {"error": str(e), "mode": "live"}
    
    return {
        "mode": "stub",
        "success": True,
        "vault_reference": f"VAULT_{session_id}",
        "file_size": f"{len(recording_data) if recording_data else 0} bytes",
        "status": "Stored",
        "message": "Recording uploaded to secure vault (stub)",
    }


def verify_session(session_id):
    """Verify that a Video KYC session was completed successfully
    
    Returns:
        dict with verification status and agent notes
    """
    return {
        "mode": "stub",
        "success": True,
        "session_id": session_id,
        "status": "Approved",
        "verified_by": "Demo Agent",
        "verified_on": str(today()),
        "agent_notes": "Customer identity verified via video KYC",
        "message": "Video KYC session verified (stub)",
    }


def _live_create_session(settings, customer_name, agent_name=None):
    """Live: Create VKYC session via API"""
    import requests
    try:
        response = requests.post(
            f"{settings.video_kyc_api_key}/session",
            json={"customer_name": customer_name, "agent": agent_name},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"Video KYC session creation failed: {e}", "Video KYC")
        return {"error": str(e), "mode": "live"}
