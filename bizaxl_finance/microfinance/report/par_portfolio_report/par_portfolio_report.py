import frappe
from frappe import _
def execute(filters=None):
    columns = [
        {"label": _("Center"), "fieldname": "center_name", "fieldtype": "Data", "width": 150},
        {"label": _("Branch"), "fieldname": "branch", "fieldtype": "Data", "width": 120},
        {"label": _("Total Members"), "fieldname": "total_members", "fieldtype": "Int", "width": 100},
        {"label": _("Active Members"), "fieldname": "active_members", "fieldtype": "Int", "width": 100},
        {"label": _("Total Portfolio"), "fieldname": "total_portfolio", "fieldtype": "Currency", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80},
    ]
    data = frappe.db.sql("""SELECT center_name, branch, total_members, active_members,
        total_portfolio, status FROM `tabMFI Center` ORDER BY center_name""", as_dict=True)
    return columns, data