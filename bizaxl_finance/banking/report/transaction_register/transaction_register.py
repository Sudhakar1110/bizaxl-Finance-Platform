import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "name", "label": _("Transaction ID"), "fieldtype": "Link", "options": "Transaction", "width": 180},
        {"fieldname": "transaction_date", "label": _("Date"), "fieldtype": "Datetime", "width": 150},
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Bizaxl Customer", "width": 200},
        {"fieldname": "transaction_type", "label": _("Type"), "fieldtype": "Data", "width": 120},
        {"fieldname": "transaction_category", "label": _("Category"), "fieldtype": "Data", "width": 120},
        {"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "from_account", "label": _("From Account"), "fieldtype": "Link", "options": "Bank Account", "width": 150},
        {"fieldname": "to_account", "label": _("To Account"), "fieldtype": "Link", "options": "Bank Account", "width": 150},
        {"fieldname": "description", "label": _("Description"), "fieldtype": "Data", "width": 250},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "reference_number", "label": _("Reference"), "fieldtype": "Data", "width": 150},
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql("""
        SELECT
            name, transaction_date, customer, transaction_type,
            transaction_category, amount, from_account, to_account,
            description, status, reference_number
        FROM `tabTransaction`
        WHERE docstatus = 1 {conditions}
        ORDER BY transaction_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data

def get_conditions(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND DATE(transaction_date) >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND DATE(transaction_date) <= %(to_date)s"
        if filters.get("customer"):
            conditions += " AND customer = %(customer)s"
        if filters.get("transaction_type"):
            conditions += " AND transaction_type = %(transaction_type)s"
        if filters.get("status"):
            conditions += " AND status = %(status)s"
    return conditions
