import frappe
from frappe import _
def execute(filters=None):
    columns = [
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("NPA Category"), "fieldname": "npa_category", "fieldtype": "Data", "width": 120},
        {"label": _("Asset Classification"), "fieldname": "asset_classification", "fieldtype": "Data", "width": 150},
        {"label": _("DPD"), "fieldname": "dpd_days", "fieldtype": "Int", "width": 80},
        {"label": _("Outstanding"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Provision %"), "fieldname": "provision_percentage", "fieldtype": "Percent", "width": 80},
        {"label": _("Provision Amount"), "fieldname": "provision_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("NPA Date"), "fieldname": "npa_date", "fieldtype": "Date", "width": 100},
    ]
    data = frappe.db.sql("""SELECT customer_name, npa_category, asset_classification, dpd_days,
        outstanding_amount, provision_percentage, provision_amount, npa_date
        FROM `tabNPA Classification` ORDER BY classification_date DESC""", as_dict=True)
    return columns, data