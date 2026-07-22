import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Pledge ID"), "fieldname": "name", "fieldtype": "Link", "options": "Gold Pledge", "width": 150},
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Loan Amount"), "fieldname": "loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Gold Value"), "fieldname": "total_gold_value", "fieldtype": "Currency", "width": 120},
        {"label": _("LTV Ratio"), "fieldname": "ltv_ratio", "fieldtype": "Percent", "width": 80},
        {"label": _("Market Rate/gm"), "fieldname": "market_rate_per_gram", "fieldtype": "Currency", "width": 100},
        {"label": _("Valuation Date"), "fieldname": "valuation_date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Branch"), "fieldname": "branch", "fieldtype": "Data", "width": 120},
        {"label": _("LTV Breach"), "fieldname": "ltv_breach", "fieldtype": "Data", "width": 80},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("status"):
            conditions += " AND status = %(status)s"
        if filters.get("branch"):
            conditions += " AND branch = %(branch)s"

    data = frappe.db.sql("""
        SELECT name, customer_name, loan_amount, total_gold_value, ltv_ratio,
               market_rate_per_gram, valuation_date, status, branch,
               CASE WHEN ltv_ratio > 75 THEN 'Yes' ELSE 'No' END as ltv_breach
        FROM `tabGold Pledge`
        WHERE docstatus < 2 {conditions}
        ORDER BY ltv_ratio DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
