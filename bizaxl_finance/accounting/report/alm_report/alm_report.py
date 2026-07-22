import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Fund"), "fieldname": "fund_name", "fieldtype": "Data", "width": 180},
        {"label": _("Fund Type"), "fieldname": "fund_type", "fieldtype": "Data", "width": 130},
        {"label": _("Current Balance"), "fieldname": "current_balance", "fieldtype": "Currency", "width": 120},
        {"label": _("Allocated"), "fieldname": "allocated_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Available for Lending"), "fieldname": "available_balance", "fieldtype": "Currency", "width": 140},
        {"label": _("Source"), "fieldname": "source", "fieldtype": "Data", "width": 150},
        {"label": _("Active"), "fieldname": "is_active", "fieldtype": "Data", "width": 60},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("fund_type"):
            conditions += " AND fund_type = %(fund_type)s"
        if filters.get("is_active"):
            conditions += " AND is_active = 1"

    data = frappe.db.sql("""
        SELECT fund_name, fund_type, current_balance, allocated_amount,
               available_balance, source,
               CASE WHEN is_active = 1 THEN 'Yes' ELSE 'No' END as is_active
        FROM `tabFund Account`
        WHERE docstatus < 2 {conditions}
        ORDER BY fund_type, current_balance DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return columns, data
