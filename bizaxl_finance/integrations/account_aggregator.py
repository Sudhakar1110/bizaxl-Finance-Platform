"""Account Aggregator (Sahamati) Integration

Fetches bank statements via consent-based Account Aggregator framework.
Stub-to-live pattern as per Sahamati AA specifications.

Spec: https://sahamati.org.in/
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def request_consent(customer_id, purpose="Loan Underwriting", duration_days=365):
    """Step 1: Request customer consent for data fetch via AA
    
    Args:
        customer_id: Bizaxl Customer name
        purpose: Purpose of data request
        duration_days: Consent validity in days
        
    Returns:
        dict with consent_handle_url (to send to customer)
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.aa_client_id:
        return _live_request_consent(settings, customer_id, purpose, duration_days)
    return _stub_request_consent(customer_id, purpose, duration_days)


def fetch_bank_statements(consent_id, months=12):
    """Step 2: Fetch bank statement data using consented access
    
    Args:
        consent_id: ID from successful consent
        months: Number of months of data to fetch
        
    Returns:
        dict with transaction data and FOIR calculation inputs
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.aa_client_id:
        return _live_fetch_statements(settings, consent_id, months)
    return _stub_fetch_statements(consent_id, months)


def auto_calc_foir(statement_data):
    """Auto-calculate FOIR from bank statement data
    
    FOIR = (Existing Obligations + Proposed EMI) / Net Monthly Income
    """
    if not statement_data or not statement_data.get("success"):
        return {"foir": 0, "income": 0, "obligations": 0}
    
    data = statement_data.get("data", {})
    total_credits = data.get("total_credits", 0)
    total_debits = data.get("total_debits", 0)
    existing_emis = data.get("existing_emis", 0)
    months = data.get("months_analyzed", 12)
    
    monthly_income = total_credits / max(months, 1)
    monthly_obligations = existing_emis / max(months, 1)
    
    foir = (monthly_obligations / monthly_income * 100) if monthly_income > 0 else 100
    
    return {
        "foir": round(foir, 2),
        "net_monthly_income": round(monthly_income, 2),
        "existing_monthly_obligations": round(monthly_obligations, 2),
        "available_for_emi": round(monthly_income - monthly_obligations, 2),
        "months_analyzed": months,
    }


def _stub_request_consent(customer_id, purpose, duration_days):
    """Stub: Simulate consent request"""
    return {
        "mode": "stub",
        "success": True,
        "consent_handle_url": f"https://aa-stub.bizaxl.com/consent/{customer_id}",
        "consent_id": f"STUB_CONSENT_{now_datetime().strftime('%Y%m%d%H%M%S')}",
        "message": "Consent URL generated (stub). Send to customer for approval.",
        "timestamp": str(now_datetime()),
    }


def _stub_fetch_statements(consent_id, months=12):
    """Stub: Simulate bank statement data"""
    import random
    
    # Generate realistic monthly data
    monthly_salary = 75000
    transactions = []
    for m in range(min(months, 12)):
        transactions.append({"month": f"2024-{m+1:02d}", "credits": monthly_salary + random.randint(0, 5000)})
    
    return {
        "mode": "stub",
        "success": True,
        "data": {
            "total_credits": monthly_salary * months,
            "total_debits": monthly_salary * months * 0.7,
            "existing_emis": 15000 * months,
            "months_analyzed": months,
            "monthly_breakdown": transactions,
            "bounce_incidents": 0,
            "average_monthly_balance": 45000,
        },
        "message": f"Bank statement fetched ({months} months, stub)",
        "timestamp": str(now_datetime()),
    }


def _live_request_consent(settings, customer_id, purpose, duration_days):
    """Live: Request consent via AA API"""
    import requests
    try:
        response = requests.post(
            f"{settings.aa_endpoint}/consent",
            json={
                "customer": customer_id,
                "purpose": purpose,
                "duration": duration_days,
                "consent_type": "FIP",
                "data_range": {"from": "12", "unit": "months"},
            },
            headers={
                "client_id": settings.aa_client_id,
                "client_secret": settings.get_password("aa_client_secret"),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"AA consent request failed: {e}", "Account Aggregator")
        return {"error": str(e), "mode": "live"}


def _live_fetch_statements(settings, consent_id, months=12):
    """Live: Fetch statements via AA API"""
    import requests
    try:
        response = requests.post(
            f"{settings.aa_endpoint}/fetch",
            json={"consent_id": consent_id, "months": months},
            headers={
                "client_id": settings.aa_client_id,
                "client_secret": settings.get_password("aa_client_secret"),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"AA fetch failed: {e}", "Account Aggregator")
        return {"error": str(e), "mode": "live"}
