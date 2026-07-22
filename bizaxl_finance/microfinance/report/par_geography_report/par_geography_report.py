import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Center"), "fieldname": "center_name", "fieldtype": "Data", "width": 150},
        {"label": _("Village"), "fieldname": "village", "fieldtype": "Data", "width": 120},
        {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 100},
        {"label": _("Field Officer"), "fieldname": "field_officer", "fieldtype": "Data", "width": 150},
        {"label": _("Total Members"), "fieldname": "total_members", "fieldtype": "Int", "width": 80},
        {"label": _("Active Members"), "fieldname": "active_members", "fieldtype": "Int", "width": 80},
        {"label": _("Total Portfolio"), "fieldname": "total_portfolio", "fieldtype": "Currency", "width": 120},
        {"label": _("PAR %"), "fieldname": "par_percentage", "fieldtype": "Percent", "width": 80},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("district"):
            conditions += " AND district = %(district)s"
        if filters.get("state"):
            conditions += " AND state = %(state)s"
        if filters.get("field_officer"):
            conditions += " AND field_officer = %(field_officer)s"
        if filters.get("status"):
            conditions += " AND status = %(status)s"

    data = frappe.db.sql("""
        SELECT
            c.center_name, c.village, c.district, c.state,
            c.field_officer, c.total_members, c.active_members,
            c.total_portfolio,
            COALESCE(
                (SELECT AVG(j.par_percentage) FROM `tabJLG Group` j WHERE j.center = c.name AND j.status = 'Active'),
                0
            ) as par_percentage,
            c.status
        FROM `tabMFI Center` c
        WHERE c.docstatus < 2 {conditions}
        ORDER BY c.state, c.district, c.center_name
    """.format(conditions=conditions), filters, as_dict=1)
    return data
