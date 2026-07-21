"""PMAY / NHB — Home Loan Subsidy Integration

Pradhan Mantri Awas Yojana (PMAY) CLSS subsidy processing.
Eligibility check, NHB/HUDCO nodal submission, and subsidy tracking.

Reference: https://pmaymis.gov.in/
NHB Guidelines: PMAY-CLSS for MIG, LIG, EWS categories
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def check_clss_eligibility(income_category, is_first_home, has_aadhaar):
    """Check CLSS subsidy eligibility
    
    CLSS Eligibility:
    - EWS: Income up to Rs.3L — Subsidy: Rs.2.67L
    - LIG: Income Rs.3L-6L — Subsidy: Rs.2.67L
    - MIG-I: Income Rs.6L-12L — Subsidy: Rs.2.35L
    - MIG-II: Income Rs.12L-18L — Subsidy: Rs.2.35L
    
    Returns:
        dict with eligibility, subsidy amount, and next steps
    """
    income_map = {
        "EWS (Up to Rs.3L)": {"limit": 300000, "subsidy": 266000},
        "LIG (Rs.3L-6L)": {"limit": 600000, "subsidy": 266000},
        "MIG-I (Rs.6L-12L)": {"limit": 1200000, "subsidy": 235000},
        "MIG-II (Rs.12L-18L)": {"limit": 1800000, "subsidy": 235000},
    }
    
    eligible = is_first_home and has_aadhaar and income_category in income_map
    subsidy_amount = income_map.get(income_category, {}).get("subsidy", 0) if eligible else 0
    
    return {
        "mode": "stub",
        "success": True,
        "eligible": eligible,
        "income_category": income_category,
        "subsidy_amount": subsidy_amount,
        "scheme": "CLSS",
        "is_first_home": is_first_home,
        "message": "CLSS eligibility: Eligible (stub)" if eligible else "Not eligible for CLSS (stub)",
    }


def submit_to_nhb(pmay_application_id, applicant_details, loan_details):
    """Submit subsidy claim to NHB/HUDCO nodal bank
    
    Args:
        pmay_application_id: Internal PMAY Application ID
        applicant_details: Applicant name, Aadhaar, income
        loan_details: Loan account, amount, property address
        
    Returns:
        dict with NHB submission reference
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.pmay_api_key:
        return _live_submit_nhb(settings, pmay_application_id, applicant_details, loan_details)
    
    return {
        "mode": "stub",
        "success": True,
        "nhb_reference": f"NHB_STUB_{today().replace('-', '')}",
        "nodal_bank": "SBI — NHB Nodal Branch",
        "status": "Submitted to NHB",
        "submitted_on": str(today()),
        "message": f"CLSS subsidy claim submitted to NHB for {applicant_details.get('name', 'Applicant')} (stub)",
    }


def track_nhb_status(nhb_reference):
    """Track the status of NHB subsidy processing"""
    return {
        "mode": "stub",
        "success": True,
        "nhb_reference": nhb_reference,
        "status": "NHB Approved",
        "subsidy_credited": True,
        "credited_on": str(today()),
        "credited_amount": 266000,
        "message": "CLSS subsidy credited to loan account (stub)",
    }


def _live_submit_nhb(settings, pmay_application_id, applicant_details, loan_details):
    """Live: Submit to NHB via PMAY portal API"""
    import requests
    try:
        response = requests.post(
            f"{settings.pmay_api_key}/clss/submit",
            json={
                "application_id": pmay_application_id,
                "applicant": applicant_details,
                "loan": loan_details,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"PMAY/NHB submission failed: {e}", "PMAY")
        return {"error": str(e), "mode": "live"}
