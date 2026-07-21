"""AI/ML Scorecard Engine Integration

Configurable ML scorecard per vertical for auto-decisioning and offer generation.
Supports pre-trained models (PMML, pickle) and API-based scoring.

Used by: All 12 lending verticals for credit assessment.
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime
import json


def calculate_risk_score(customer_data, vertical="Personal Loan"):
    """Calculate risk score for a customer using ML scorecard
    
    Args:
        customer_data: dict with customer attributes
            - bureau_score, income, age, employment_type
            - existing_obligations, loan_amount, tenure
        vertical: Lending vertical (Personal Loan, Business Loan, etc.)
        
    Returns:
        dict with risk score, grade, and decision
    """
    settings = frappe.get_single_doc("Integration Settings")
    
    if settings.scorecard_enabled and settings.scorecard_model_path:
        return _live_score(settings, customer_data, vertical)
    return _stub_score(customer_data, vertical)


def generate_offer(customer_data, risk_score):
    """Generate loan offer based on risk profile
    
    Args:
        customer_data: Customer details
        risk_score: Risk score from calculate_risk_score()
        
    Returns:
        dict with offer details (amount, rate, tenure)
    """
    score = risk_score.get("score", 500)
    grade = risk_score.get("grade", "C")
    
    # Sample offer generation based on risk grade
    offer_map = {
        "A+": {"multiplier": 25, "rate": 9.5, "tenure": 60},
        "A": {"multiplier": 20, "rate": 10.5, "tenure": 48},
        "B": {"multiplier": 15, "rate": 12.0, "tenure": 36},
        "C": {"multiplier": 10, "rate": 14.5, "tenure": 24},
        "D": {"multiplier": 5, "rate": 18.0, "tenure": 12},
    }
    
    offer_params = offer_map.get(grade, offer_map["C"])
    monthly_income = customer_data.get("monthly_income", 50000)
    proposed_amount = monthly_income * offer_params["multiplier"]
    
    return {
        "mode": "stub",
        "success": True,
        "risk_grade": grade,
        "risk_score": score,
        "offer": {
            "proposed_amount": proposed_amount,
            "interest_rate": offer_params["rate"],
            "max_tenure_months": offer_params["tenure"],
            "processing_fee_pct": 2.0,
        },
        "auto_approved": grade in ("A+", "A", "B"),
        "message": f"Offer generated: ₹{proposed_amount:,.2f} @ {offer_params['rate']}% for {offer_params['tenure']} months",
    }


def ml_scorecard_predict(model_path, features):
    """Run prediction using a pre-trained ML model
    
    In production: Uses joblib/pickle to load the model.
    Supports scikit-learn, XGBoost, LightGBM models.
    
    Args:
        model_path: Path to the model file (.pkl)
        features: Feature vector for prediction
        
    Returns:
        dict with prediction results
    """
    try:
        # Production implementation:
        # import joblib
        # model = joblib.load(model_path)
        # prediction = model.predict(features)
        # probability = model.predict_proba(features)
        
        # Stub: Return simulated prediction
        import numpy as np
        simulated_score = 650 + (hash(str(features)) % 250)
        return {
            "mode": "stub",
            "success": True,
            "prediction": min(max(simulated_score, 300), 900),
            "probability_default": round(100 - simulated_score / 9, 2),
            "model": model_path.split("/")[-1],
        }
    except ImportError:
        return {"error": "ML libraries not installed", "mode": "stub"}
    except Exception as e:
        return {"error": str(e), "mode": "stub"}


def _stub_score(customer_data, vertical="Personal Loan"):
    """Stub: Simulate scorecard-based risk assessment"""
    bureau_score = customer_data.get("bureau_score", 700)
    income = customer_data.get("monthly_income", 50000)
    existing_obligations = customer_data.get("existing_monthly_obligations", 0)
    loan_amount = customer_data.get("loan_amount", 500000)
    
    # Simple score calculation (in production: ML model)
    score = bureau_score
    foir = (existing_obligations / income * 100) if income > 0 else 50
    
    if foir > 50:
        score -= 100
    elif foir > 30:
        score -= 50
    
    if loan_amount > income * 20:
        score -= 50
    
    score = max(300, min(900, score))
    
    if score >= 800:
        grade = "A+"
    elif score >= 750:
        grade = "A"
    elif score >= 650:
        grade = "B"
    elif score >= 550:
        grade = "C"
    else:
        grade = "D"
    
    return {
        "mode": "stub",
        "success": True,
        "score": score,
        "grade": grade,
        "foir": round(foir, 2),
        "bureau_score_used": bureau_score,
        "vertical": vertical,
        "decision": "Auto-Approve" if grade in ("A+", "A", "B") else "Manual Review Required",
        "message": f"Risk assessment completed: Grade {grade} (stub)",
    }


def _live_score(settings, customer_data, vertical="Personal Loan"):
    """Live: Score via ML model API endpoint"""
    import requests
    try:
        response = requests.post(
            settings.scorecard_endpoint,
            json={
                "features": customer_data,
                "vertical": vertical,
                "model": settings.scorecard_model_path,
            },
            headers={"Authorization": f"Bearer {settings.get_password('scorecard_auth_token')}"},
            timeout=settings.scorecard_timeout or 30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"Scorecard prediction failed: {e}", "Scorecard")
        return {"error": str(e), "mode": "live"}
