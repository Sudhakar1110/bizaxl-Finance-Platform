import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Report Name"), "fieldname": "report_name", "fieldtype": "Data", "width": 200},
        {"label": _("Report Type"), "fieldname": "report_type", "fieldtype": "Data", "width": 150},
        {"label": _("Period"), "fieldname": "reporting_period", "fieldtype": "Data", "width": 100},
        {"label": _("Period Start"), "fieldname": "period_start", "fieldtype": "Date", "width": 100},
        {"label": _("Period End"), "fieldname": "period_end", "fieldtype": "Date", "width": 100},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
        {"label": _("Submission Date"), "fieldname": "submission_date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND period_start >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND period_end <= %(to_date)s"
        if filters.get("status"):
            conditions += " AND status = %(status)s"

    # Filter for FIU-IND related report types
    data = frappe.db.sql("""
        SELECT report_name, report_type, reporting_period, period_start, period_end,
               due_date, submission_date, status
        FROM `tabRegulatory Report`
        WHERE report_type IN ('FIU-IND CTR', 'FIU-IND STR')
        {conditions}
        ORDER BY period_end DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
