import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Member"), "fieldname": "member_name", "fieldtype": "Data", "width": 150},
        {"label": _("Center"), "fieldname": "center", "fieldtype": "Data", "width": 120},
        {"label": _("Group"), "fieldname": "jlg_group", "fieldtype": "Data", "width": 120},
        {"label": _("Loan Cycle"), "fieldname": "current_cycle", "fieldtype": "Int", "width": 80},
        {"label": _("Total Outstanding"), "fieldname": "total_outstanding", "fieldtype": "Currency", "width": 120},
        {"label": _("Loan Amount"), "fieldname": "loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Overdue Days"), "fieldname": "overdue_days", "fieldtype": "Int", "width": 80},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("center"):
            conditions += " AND m.center = %(center)s"
        if filters.get("status"):
            conditions += " AND m.status = %(status)s"

    data = frappe.db.sql("""
        SELECT
            m.member_name, m.center, m.jlg_group,
            (SELECT j.current_cycle FROM `tabJLG Group` j WHERE j.name = m.jlg_group) as current_cycle,
            COALESCE(m.total_outstanding, 0) as total_outstanding,
            COALESCE(m.loan_amount, 0) as loan_amount,
            m.overdue_days, m.status
        FROM `tabMFI Member` m
        WHERE m.docstatus < 2 {conditions}
        ORDER BY m.total_outstanding DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
