import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Alert Type"), "fieldname": "alert_type", "fieldtype": "Data", "width": 130},
        {"label": _("Severity"), "fieldname": "severity", "fieldtype": "Data", "width": 80},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Alert Date"), "fieldname": "alert_date", "fieldtype": "Date", "width": 100},
        {"label": _("Investigator"), "fieldname": "investigator", "fieldtype": "Data", "width": 150},
        {"label": _("Disposition"), "fieldname": "disposition", "fieldtype": "Data", "width": 120},
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 250},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND alert_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND alert_date <= %(to_date)s"
        if filters.get("severity"):
            conditions += " AND severity = %(severity)s"
        if filters.get("status"):
            conditions += " AND status = %(status)s"
        if filters.get("alert_type"):
            conditions += " AND alert_type = %(alert_type)s"

    data = frappe.db.sql("""
        SELECT customer_name, alert_type, severity, status, alert_date,
               investigator, disposition, description
        FROM `tabFraud Alert`
        WHERE docstatus < 2 {conditions}
        ORDER BY alert_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
