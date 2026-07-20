import frappe
from frappe import _
def execute(filters=None):
    columns = [
        {"label": _("Date"), "fieldname": "collection_date", "fieldtype": "Date", "width": 100},
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Type"), "fieldname": "collection_type", "fieldtype": "Data", "width": 120},
        {"label": _("Amount Due"), "fieldname": "amount_due", "fieldtype": "Currency", "width": 120},
        {"label": _("Amount Collected"), "fieldname": "amount_collected", "fieldtype": "Currency", "width": 120},
        {"label": _("Officer"), "fieldname": "field_officer", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.db.sql("""SELECT collection_date, customer_name, collection_type, amount_due,
        amount_collected, field_officer, status FROM `tabCollection Record`
        WHERE docstatus < 2 ORDER BY collection_date DESC""", as_dict=True)
    return columns, data