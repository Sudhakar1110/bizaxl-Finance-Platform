import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("User"), "fieldname": "user", "fieldtype": "Data", "width": 150},
        {"label": _("Document Type"), "fieldname": "ref_doctype", "fieldtype": "Data", "width": 150},
        {"label": _("Document Name"), "fieldname": "doc_name", "fieldtype": "Dynamic Link", "options": "ref_doctype", "width": 180},
        {"label": _("Action"), "fieldname": "action", "fieldtype": "Data", "width": 100},
        {"label": _("Timestamp"), "fieldname": "creation", "fieldtype": "Datetime", "width": 160},
        {"label": _("IP Address"), "fieldname": "ip_address", "fieldtype": "Data", "width": 120},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND creation >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND creation <= %(to_date)s"
        if filters.get("user"):
            conditions += " AND owner = %(user)s"
        if filters.get("ref_doctype"):
            conditions += " AND ref_doctype = %(ref_doctype)s"

    # Uses Frappe's built-in Todo/DocType tracking via tabVersion
    data = frappe.db.sql("""
        SELECT
            v.owner as user,
            v.ref_doctype,
            v.docname as doc_name,
            v.data as action,
            v.creation,
            v.ip_address
        FROM `tabVersion` v
        WHERE v.docstatus < 2 {conditions}
        ORDER BY v.creation DESC
        LIMIT 1000
    """.format(conditions=conditions), filters, as_dict=1)
    return data
