import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Screening Type"), "fieldname": "screening_type", "fieldtype": "Data", "width": 120},
        {"label": _("Screening List"), "fieldname": "screening_list", "fieldtype": "Data", "width": 120},
        {"label": _("Risk Level"), "fieldname": "risk_level", "fieldtype": "Data", "width": 80},
        {"label": _("Verification Status"), "fieldname": "verification_status", "fieldtype": "Data", "width": 120},
        {"label": _("Screening Date"), "fieldname": "screening_date", "fieldtype": "Date", "width": 100},
        {"label": _("Verified By"), "fieldname": "verified_by", "fieldtype": "Data", "width": 150},
        {"label": _("PAN"), "fieldname": "pan", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND screening_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND screening_date <= %(to_date)s"
        if filters.get("risk_level"):
            conditions += " AND risk_level = %(risk_level)s"
        if filters.get("verification_status"):
            conditions += " AND verification_status = %(verification_status)s"

    data = frappe.db.sql("""
        SELECT customer_name, screening_type, screening_list, risk_level,
               verification_status, screening_date, verified_by, pan
        FROM `tabAML Screening`
        WHERE docstatus < 2 {conditions}
        ORDER BY screening_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
