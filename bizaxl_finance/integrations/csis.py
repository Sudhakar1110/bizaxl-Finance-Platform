"""CSIS — Education Loan Interest Subsidy Integration

Central Sector Interest Subsidy Scheme (CSIS) for education loans.
Handles eligibility check, subsidy claim submission, and status tracking.

Reference: https://www.buddy4study.com/
Department of Higher Education, Ministry of Education
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def check_eligibility(family_income, course_type, institution_type):
    """Check student eligibility for CSIS
    
    CSIS Eligibility:
    - Family income up to Rs.8L per annum
    - Professional/technical courses
    - Recognized institutions in India
    
    Returns:
        dict with eligibility status and subsidy amount
    """
    eligible = (
        family_income and family_income <= 800000
        and course_type in ("Graduate", "Post Graduate", "PhD", "Diploma")
    )
    
    subsidy_amount = 0
    if eligible:
        # 2% interest subsidy during moratorium period
        if family_income <= 450000:
            subsidy_amount = 50000  # Full subsidy
        else:
            subsidy_amount = 20000  # Partial subsidy
    
    return {
        "mode": "stub",
        "success": True,
        "eligible": eligible,
        "subsidy_amount": subsidy_amount,
        "scheme": "CSIS",
        "income_slab": "Up to Rs.4.5L" if family_income <= 450000 else "Rs.4.5L - Rs.8L",
        "message": "CSIS eligibility checked (stub)" if eligible else "Not eligible for CSIS (stub)",
    }


def submit_subsidy_claim(csis_application_id, student_details, loan_details):
    """Submit CSIS subsidy claim to nodal bank / portal
    
    Args:
        csis_application_id: Internal CSIS Application ID
        student_details: Student name, institution, course, income
        loan_details: Loan account, amount, sanction date
        
    Returns:
        dict with claim reference
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.csis_api_key:
        return _live_submit_claim(settings, csis_application_id, student_details, loan_details)
    
    return {
        "mode": "stub",
        "success": True,
        "claim_reference": f"CSIS_CLM_{today().replace('-', '')}_{csis_application_id[-6:]}",
        "status": "Submitted to Nodal Bank",
        "submitted_on": str(today()),
        "message": f"CSIS subsidy claim submitted for {student_details.get('student_name', 'Student')} (stub)",
    }


def track_status(claim_reference):
    """Track the status of a submitted CSIS claim"""
    return {
        "mode": "stub",
        "success": True,
        "claim_reference": claim_reference,
        "status": "Under Process at Nodal Bank",
        "last_updated": str(today()),
        "estimated_processing_days": 30,
        "message": "CSIS claim status: Under Process (stub)",
    }


def _live_submit_claim(settings, csis_application_id, student_details, loan_details):
    """Live: Submit CSIS claim via portal API"""
    import requests
    try:
        response = requests.post(
            f"{settings.csis_api_key}/claim",
            json={
                "application_id": csis_application_id,
                "student": student_details,
                "loan": loan_details,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"CSIS claim submission failed: {e}", "CSIS")
        return {"error": str(e), "mode": "live"}
