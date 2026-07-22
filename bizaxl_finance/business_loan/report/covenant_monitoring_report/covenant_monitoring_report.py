import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Covenant Type"), "fieldname": "covenant_type", "fieldtype": "Data", "width": 150},
        {"label": _("Required Value"), "fieldname": "required_value", "fieldtype": "Float", "width": 100},
        {"label": _("Actual Value"), "fieldname": "actual_value", "fieldtype": "Float", "width": 100},
        {"label": _("Frequency"), "fieldname": "frequency", "fieldtype": "Data", "width": 80},
        {"label": _("Last Monitored"), "fieldname": "last_monitored_date", "fieldtype": "Date", "width": 100},
        {"label": _("Next Monitoring"), "fieldname": "next_monitoring_date", "fieldtype": "Date", "width": 100},
        {"label": _("Compliance Status"), "fieldname": "compliance_status", "fieldtype": "Data", "width": 120},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("compliance_status"):
            conditions += " AND compliance_status = %(compliance_status)s"
        if filters.get("covenant_type"):
            conditions += " AND covenant_type = %(covenant_type)s"

    data = frappe.db.sql("""
        SELECT
            lc.covenant_type, lc.required_value, lc.actual_value,
            lc.frequency,
            lc.last_monitored_date, lc.next_monitoring_date,
            lc.compliance_status, lc.remarks
        FROM `tabLoan Covenant` lc
        WHERE lc.docstatus < 2 {conditions}
        ORDER BY
            CASE lc.compliance_status
                WHEN 'Critical Breach' THEN 1
                WHEN 'Breached' THEN 2
                WHEN 'Not Monitored' THEN 3
                ELSE 4
            END,
            lc.next_monitoring_date ASC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
