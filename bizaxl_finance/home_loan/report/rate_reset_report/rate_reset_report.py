import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Bizaxl Customer", "width": 150},
        {"label": _("Loan Application"), "fieldname": "loan_application", "fieldtype": "Link", "options": "Loan Application", "width": 150},
        {"label": _("Reset Date"), "fieldname": "reset_date", "fieldtype": "Date", "width": 100},
        {"label": _("Reset Reason"), "fieldname": "reset_reason", "fieldtype": "Data", "width": 130},
        {"label": _("Previous Rate"), "fieldname": "previous_rate", "fieldtype": "Percent", "width": 80},
        {"label": _("New Rate"), "fieldname": "new_rate", "fieldtype": "Percent", "width": 80},
        {"label": _("Previous EMI"), "fieldname": "previous_emi", "fieldtype": "Currency", "width": 120},
        {"label": _("New EMI"), "fieldname": "new_emi", "fieldtype": "Currency", "width": 120},
        {"label": _("Outstanding Principal"), "fieldname": "outstanding_principal", "fieldtype": "Currency", "width": 130},
        {"label": _("Rate Type"), "fieldname": "rate_type", "fieldtype": "Data", "width": 120},
        {"label": _("Notified"), "fieldname": "notified_to_customer", "fieldtype": "Data", "width": 80},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND reset_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND reset_date <= %(to_date)s"
        if filters.get("reset_reason"):
            conditions += " AND reset_reason = %(reset_reason)s"
        if filters.get("rate_type"):
            conditions += " AND rate_type = %(rate_type)s"

    data = frappe.db.sql("""
        SELECT customer, loan_application, reset_date, reset_reason,
               previous_rate, new_rate, previous_emi, new_emi,
               outstanding_principal, rate_type,
               CASE WHEN notified_to_customer = 1 THEN 'Yes' ELSE 'No' END as notified_to_customer
        FROM `tabRate Reset Log`
        WHERE docstatus < 2 {conditions}
        ORDER BY reset_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return columns, data
