import frappe
from frappe import _
def execute(filters=None):
    columns = [
        {"label": _("Chit Name"), "fieldname": "chit_name", "fieldtype": "Data", "width": 180},
        {"label": _("Chit Value"), "fieldname": "chit_value", "fieldtype": "Currency", "width": 120},
        {"label": _("Monthly Sub"), "fieldname": "monthly_subscription", "fieldtype": "Currency", "width": 120},
        {"label": _("Members"), "fieldname": "number_of_members", "fieldtype": "Int", "width": 80},
        {"label": _("Duration"), "fieldname": "duration_months", "fieldtype": "Int", "width": 80},
        {"label": _("Foreman"), "fieldname": "foreman_name", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.db.sql("""SELECT chit_name, chit_value, monthly_subscription, number_of_members,
        duration_months, foreman_name, status FROM `tabChit Group` ORDER BY creation DESC""", as_dict=True)
    return columns, data