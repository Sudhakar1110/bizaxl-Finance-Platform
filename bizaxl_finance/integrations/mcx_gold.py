"""MCX — Live Gold Rate Integration

Fetches real-time MCX gold rate for LTV calculation and daily monitoring.
Stub-to-live pattern — works without API key for testing.

Reference: MCX India, IBJA (India Bullion & Jewellers Association)
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime


def fetch_live_rate():
    """Fetch current MCX gold rate
    
    Returns:
        dict with gold rate per 10 grams and other PM rates
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.mcx_api_key:
        return _live_fetch_rate(settings)
    
    return _stub_fetch_rate()


def get_historical_rates(days=30):
    """Get historical gold rates for the last N days
    
    Used for LTV trend monitoring.
    """
    import random
    base_rate = 6500
    historical = []
    
    for d in range(days):
        fluctuation = random.uniform(-150, 150)
        historical.append({
            "date": f"{today()[:8]}{d+1:02d}",
            "rate_per_10g": round(base_rate + fluctuation, 2),
        })
    
    return {
        "mode": "stub",
        "success": True,
        "data": historical,
        "message": f"Historical rates for last {days} days (stub)",
    }


def calculate_ltv(gold_weight_grams, purity_karat, loan_amount=None):
    """Calculate LTV based on current gold rate
    
    RBI Gold Loan LTV: Max 75% (for all NBFCs and banks)
    
    Args:
        gold_weight_grams: Net weight in grams
        purity_karat: 18K, 22K, or 24K
        loan_amount: Optional — to calculate current LTV %
        
    Returns:
        dict with gold value, max loan, and LTV %
    """
    rate_data = fetch_live_rate()
    if not rate_data.get("success"):
        return {"error": "Unable to fetch gold rate"}
    
    rate_per_10g = rate_data.get("data", {}).get("rate_per_10g", 6500)
    rate_per_gram = rate_per_10g / 10
    
    # Apply purity factor
    purity_factors = {24: 1.0, 22: 0.916, 18: 0.75}
    purity_factor = purity_factors.get(purity_karat, 0.75)
    
    pure_gold_value = gold_weight_grams * rate_per_gram * purity_factor
    max_loan = pure_gold_value * 0.75  # RBI 75% max
    
    result = {
        "gold_value": round(pure_gold_value, 2),
        "max_loan": round(max_loan, 2),
        "max_ltv_pct": 75,
        "current_gold_rate_per_10g": rate_per_10g,
        "purity_factor": purity_factor,
    }
    
    if loan_amount:
        result["current_ltv_pct"] = round((loan_amount / pure_gold_value) * 100, 2)
    
    return result


def _stub_fetch_rate():
    """Stub: Return realistic MCX gold rate"""
    import random
    
    # Simulate daily fluctuation around Rs.6,500/10g (24K)
    base_rate = 6500
    fluctuation = random.uniform(-100, 100)
    
    return {
        "mode": "stub",
        "success": True,
        "data": {
            "rate_per_10g": round(base_rate + fluctuation, 2),
            "rate_per_gram": round((base_rate + fluctuation) / 10, 2),
            "currency": "INR",
            "unit": "10 Grams",
            "purity": "24K (999)",
            "exchange": "MCX",
            "timestamp": str(now_datetime()),
            "change_pct": round(fluctuation / base_rate * 100, 2),
            "high_52w": 7200,
            "low_52w": 5800,
        },
        "message": "MCX gold rate fetched (stub)",
    }


def _live_fetch_rate(settings):
    """Live: Fetch MCX gold rate via API"""
    import requests
    try:
        response = requests.get(
            settings.mcx_endpoint,
            headers={"x-api-key": settings.get_password("mcx_api_key")},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "mode": "live",
            "success": True,
            "data": data,
            "message": "MCX gold rate fetched live",
        }
    except Exception as e:
        frappe.log_error(f"MCX rate fetch failed: {e}", "MCX Gold")
        return {"error": str(e), "mode": "live"}
