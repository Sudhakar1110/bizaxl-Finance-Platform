import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Scorecard Name"), "fieldname": "scorecard_name", "fieldtype": "Data", "width": 180},
        {"label": _("Vertical"), "fieldname": "vertical", "fieldtype": "Data", "width": 130},
        {"label": _("Model Type"), "fieldname": "model_type", "fieldtype": "Data", "width": 130},
        {"label": _("Max Score"), "fieldname": "max_score", "fieldtype": "Int", "width": 80},
        {"label": _("Min Approval Score"), "fieldname": "min_score_for_approval", "fieldtype": "Int", "width": 100},
        {"label": _("Min Referral Score"), "fieldname": "min_score_for_referral", "fieldtype": "Int", "width": 100},
        {"label": _("Max Loan Amount"), "fieldname": "max_loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Auto Decision"), "fieldname": "auto_decision_enabled", "fieldtype": "Data", "width": 80},
        {"label": _("Auto Decision Max"), "fieldname": "max_auto_decision_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Offer Generation"), "fieldname": "offer_generation_enabled", "fieldtype": "Data", "width": 80},
        {"label": _("Active"), "fieldname": "is_active", "fieldtype": "Data", "width": 60},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("vertical"):
            conditions += " AND vertical = %(vertical)s"
        if filters.get("model_type"):
            conditions += " AND model_type = %(model_type)s"

    data = frappe.db.sql("""
        SELECT scorecard_name, vertical, model_type, max_score,
               min_score_for_approval, min_score_for_referral, max_loan_amount,
               CASE WHEN auto_decision_enabled = 1 THEN 'Yes' ELSE 'No' END as auto_decision_enabled,
               max_auto_decision_amount,
               CASE WHEN offer_generation_enabled = 1 THEN 'Yes' ELSE 'No' END as offer_generation_enabled,
               CASE WHEN is_active = 1 THEN 'Yes' ELSE 'No' END as is_active
        FROM `tabScorecard Config`
        WHERE docstatus < 2 {conditions}
        ORDER BY vertical, scorecard_name
    """.format(conditions=conditions), filters, as_dict=1)
    return columns, data
