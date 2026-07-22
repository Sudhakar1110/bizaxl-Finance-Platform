import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Loan Application"), "fieldname": "name", "fieldtype": "Link", "options": "Loan Application", "width": 150},
        {"label": _("Loan Amount"), "fieldname": "loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Interest Rate"), "fieldname": "interest_rate", "fieldtype": "Percent", "width": 80},
        {"label": _("Tenure (Months)"), "fieldname": "tenure_months", "fieldtype": "Int", "width": 80},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Application Date"), "fieldname": "application_date", "fieldtype": "Date", "width": 100},
        {"label": _("Risk Grade"), "fieldname": "risk_grade", "fieldtype": "Data", "width": 80},
        {"label": _("e-Sign Status"), "fieldname": "esign_status", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND application_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND application_date <= %(to_date)s"
        if filters.get("status"):
            conditions += " AND status = %(status)s"

    data = frappe.db.sql("""
        SELECT customer_name, name, loan_amount, interest_rate, tenure_months,
               status, application_date, risk_grade, esign_status
        FROM `tabLoan Application`
        WHERE docstatus < 2 {conditions}
        ORDER BY application_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
