"""Credit Bureau Integration (CIBIL / Experian / CRIF / Equifax)

Stub-to-live pattern:
    Stub: Returns realistic credit report data
    Live: Integrates with configured bureau API

All 4 bureaus supported via configurable endpoint.
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def pull_credit_report(pan_number, bureau="CIBIL"):
    """Pull credit report from bureau.
    
    Args:
        pan_number: Customer's PAN
        bureau: CIBIL, Experian, CRIF, or Equifax
        
    Returns:
        dict with credit report data (score, accounts, enquiries)
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.bureau_api_key:
        return _live_pull(settings, pan_number, bureau)
    return _stub_pull(pan_number, bureau)


def parse_bureau_response(response_data):
    """Parse bureau response into standardized format"""
    if not response_data or not response_data.get("success"):
        return None
    
    data = response_data.get("data", {})
    return {
        "bureau_name": data.get("bureau", "CIBIL"),
        "credit_score": data.get("score", 700),
        "score_range": data.get("score_range", "300-900"),
        "report_date": str(today()),
        "total_accounts": data.get("total_accounts", 0),
        "active_accounts": data.get("active_accounts", 0),
        "delinquent_accounts": data.get("delinquent_accounts", 0),
        "total_enquiries": data.get("total_enquiries", 0),
        "credit_utilization": data.get("credit_utilization", 0),
        "raw_response": response_data,
    }


def _stub_pull(pan_number, bureau="CIBIL"):
    """Stub: Simulate credit bureau report"""
    # Generate realistic score based on PAN hash for consistency
    score_hash = hash(pan_number or "DEMOPAN1234") % 201
    score = 550 + score_hash  # Score between 550-750
    
    return {
        "mode": "stub",
        "success": True,
        "data": {
            "bureau": bureau,
            "report_id": f"STUB_{bureau}_{today()}",
            "score": score,
            "score_range": "300-900",
            "total_accounts": 8,
            "active_accounts": 5,
            "delinquent_accounts": 1 if score < 650 else 0,
            "total_enquiries": 3,
            "credit_utilization": round(35 + (score % 30), 1),
            "accounts": [
                {"type": "Credit Card", "bank": "HDFC Bank", "limit": 50000, "balance": 15000, "status": "Active"},
                {"type": "Personal Loan", "bank": "ICICI Bank", "amount": 200000, "balance": 85000, "status": "Active"},
                {"type": "Home Loan", "bank": "SBI", "amount": 2500000, "balance": 2100000, "status": "Active"},
            ],
        },
        "message": f"{bureau} report retrieved (stub)",
        "timestamp": str(now_datetime()),
    }


def _live_pull(settings, pan_number, bureau="CIBIL"):
    """Live: Pull credit report from bureau API"""
    import requests
    try:
        response = requests.post(
            f"{settings.bureau_endpoint}/pull",
            json={"pan": pan_number, "bureau": bureau, "purpose": "Loan Underwriting"},
            headers={"x-api-key": settings.get_password("bureau_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"Bureau pull failed ({bureau}): {e}", "Bureau")
        return {"error": str(e), "mode": "live"}
