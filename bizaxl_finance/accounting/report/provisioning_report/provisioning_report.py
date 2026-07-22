import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("NPA Category"), "fieldname": "npa_category", "fieldtype": "Data", "width": 120},
        {"label": _("Min DPD"), "fieldname": "days_past_due_min", "fieldtype": "Int", "width": 80},
        {"label": _("Max DPD"), "fieldname": "days_past_due_max", "fieldtype": "Int", "width": 80},
        {"label": _("Provision %"), "fieldname": "provision_percentage", "fieldtype": "Percent", "width": 80},
        {"label": _("Total Outstanding"), "fieldname": "total_outstanding", "fieldtype": "Currency", "width": 130},
        {"label": _("Provision Required"), "fieldname": "provision_required", "fieldtype": "Currency", "width": 130},
        {"label": _("Is Active"), "fieldname": "is_active", "fieldtype": "Data", "width": 60},
    ]

def get_data(filters):
    data = frappe.db.sql("""
        SELECT
            pr.npa_category, pr.days_past_due_min, pr.days_past_due_max,
            pr.provision_percentage, pr.is_active,
            COALESCE(
                (SELECT SUM(npa.outstanding_amount)
                 FROM `tabNPA Classification` npa
                 WHERE npa.npa_category = pr.npa_category
                 AND npa.docstatus < 2),
                0
            ) as total_outstanding,
            ROUND(
                COALESCE(
                    (SELECT SUM(npa.outstanding_amount)
                     FROM `tabNPA Classification` npa
                     WHERE npa.npa_category = pr.npa_category
                     AND npa.docstatus < 2),
                    0
                ) * pr.provision_percentage / 100,
            2) as provision_required
        FROM `tabProvisioning Rule` pr
        ORDER BY pr.days_past_due_min
    """, as_dict=1)

    return columns, data
