import frappe
from frappe import _
def execute(filters=None):
    columns = [
        {"label": _("Property"), "fieldname": "property_address", "fieldtype": "Data", "width": 200},
        {"label": _("Type"), "fieldname": "property_type", "fieldtype": "Data", "width": 120},
        {"label": _("Area"), "fieldname": "built_up_area", "fieldtype": "Float", "width": 100},
        {"label": _("Agreed Value"), "fieldname": "agreed_value", "fieldtype": "Currency", "width": 120},
        {"label": _("Legal Status"), "fieldname": "legal_status", "fieldtype": "Data", "width": 140},
        {"label": _("Construction"), "fieldname": "construction_stage", "fieldtype": "Data", "width": 130},
    ]
    data = frappe.db.sql("""SELECT property_address, property_type, built_up_area, agreed_value,
        legal_status, construction_stage FROM `tabProperty Detail` ORDER BY creation DESC""", as_dict=True)
    return columns, data