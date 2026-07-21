"""GSTN API Integration

Fetches GST returns (GSTR-1, GSTR-3B) for MSME/Business Loan income assessment.
Stub-to-live pattern as per GSTN API specifications.

API Docs: https://api.gst.gov.in/
Reference: GST Council, GSTN
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def verify_gstin(gstin):
    """Verify GSTIN and fetch basic business details
    
    Args:
        gstin: 15-character GSTIN
        
    Returns:
        dict with business details (name, address, status)
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.gstn_api_key:
        return _live_verify_gstin(settings, gstin)
    
    # Validate format: 2-digit state + 10-digit PAN + 1-entity + 1-blank + 1-check
    if not gstin or len(gstin) != 15:
        return {"error": "Invalid GSTIN format", "mode": "stub"}
    
    return {
        "mode": "stub",
        "success": True,
        "data": {
            "gstin": gstin.upper(),
            "business_name": "Demo Business Solutions Pvt Ltd",
            "trade_name": "Demo Business",
            "address": "123, Test Layout, Bangalore - 560001",
            "state": "Karnataka",
            "registration_date": "2020-01-01",
            "status": "Active",
            "business_type": "Private Limited",
            "nature_of_business": "Trading & Manufacturing",
        },
        "message": "GSTIN verified (stub)",
    }


def fetch_gstr1(gstin, return_period):
    """Fetch GSTR-1 (Outward Supply) for a given period
    
    Args:
        gstin: GSTIN
        return_period: e.g. "MMYYYY" format
        
    Returns:
        dict with invoice data and turnover
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.gstn_api_key:
        return _live_fetch_return(settings, gstin, return_period, "GSTR1")
    
    return _stub_fetch_return(gstin, return_period, "GSTR1")


def fetch_gstr3b(gstin, return_period):
    """Fetch GSTR-3B (Summary Return) for a given period
    
    Args:
        gstin: GSTIN
        return_period: e.g. "MMYYYY" format
        
    Returns:
        dict with summarized turnover and tax data
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.gstn_api_key:
        return _live_fetch_return(settings, gstin, return_period, "GSTR3B")
    
    return _stub_fetch_return(gstin, return_period, "GSTR3B")


def assess_gst_turnover(gstin, months=12):
    """Assess total turnover from last 12-24 months of GST returns
    
    Used for MSME loan income assessment.
    """
    combined = {
        "gstin": gstin,
        "periods_analyzed": months,
        "total_turnover": 0,
        "total_tax_paid": 0,
        "monthly_breakdown": [],
    }
    
    # In production: iterate over last 12 months of returns
    for m in range(min(months, 12)):
        period = f"{m+1:02d}{today()[:4]}"
        result = fetch_gstr3b(gstin, period)
        if result.get("success"):
            combined["total_turnover"] += result.get("data", {}).get("turnover", 0)
            combined["total_tax_paid"] += result.get("data", {}).get("tax_paid", 0)
            combined["monthly_breakdown"].append({
                "period": period,
                "turnover": result.get("data", {}).get("turnover", 0),
            })
    
    combined["average_monthly_turnover"] = combined["total_turnover"] / max(months, 1)
    return combined


def _stub_fetch_return(gstin, return_period, return_type):
    """Stub: Simulate GST return data"""
    import random
    turnover = random.randint(500000, 2000000)
    tax = round(turnover * 0.12, 2)
    
    return {
        "mode": "stub",
        "success": True,
        "data": {
            "gstin": gstin.upper(),
            "return_period": return_period,
            "return_type": return_type,
            "status": "Filed",
            "turnover": turnover,
            "tax_paid": tax,
            "filing_date": str(today()),
        },
        "message": f"{return_type} for {return_period} retrieved (stub)",
    }


def _live_verify_gstin(settings, gstin):
    """Live: Verify GSTIN via GSTN API"""
    import requests
    try:
        response = requests.get(
            f"{settings.gstn_endpoint}/verify/{gstin}",
            headers={"x-api-key": settings.get_password("gstn_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"GSTIN verification failed: {e}", "GSTN")
        return {"error": str(e), "mode": "live"}


def _live_fetch_return(settings, gstin, return_period, return_type):
    """Live: Fetch GST return via GSTN API"""
    import requests
    try:
        response = requests.get(
            f"{settings.gstn_endpoint}/returns/{gstin}/{return_type}/{return_period}",
            headers={"x-api-key": settings.get_password("gstn_api_key")},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"GST return fetch failed ({return_type}): {e}", "GSTN")
        return {"error": str(e), "mode": "live"}
