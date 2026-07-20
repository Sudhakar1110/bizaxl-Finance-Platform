import frappe
from frappe import _
def execute(filters=None):
    columns = [
        {"label": _("Make/Model"), "fieldname": "make", "fieldtype": "Data", "width": 180},
        {"label": _("Category"), "fieldname": "vehicle_category", "fieldtype": "Data", "width": 120},
        {"label": _("Price"), "fieldname": "agreed_price", "fieldtype": "Currency", "width": 120},
        {"label": _("Registration"), "fieldname": "registration_number", "fieldtype": "Data", "width": 140},
        {"label": _("Hypothecation"), "fieldname": "rc_hypothecation_status", "fieldtype": "Data", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.db.sql("""SELECT make, vehicle_category, agreed_price, registration_number,
        rc_hypothecation_status, status FROM `tabVehicle Detail` ORDER BY creation DESC""", as_dict=True)
    return columns, data