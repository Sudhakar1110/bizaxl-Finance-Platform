from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "name", "label": _("Repayment ID"), "fieldtype": "Link", "options": "Loan Repayment", "width": 150},
        {"fieldname": "loan_application", "label": _("Loan Application"), "fieldtype": "Link", "options": "Loan Application", "width": 150},
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Bizaxl Customer", "width": 200},
        {"fieldname": "payment_date", "label": _("Payment Date"), "fieldtype": "Date", "width": 120},
        {"fieldname": "repayment_type", "label": _("Repayment Type"), "fieldtype": "Data", "width": 150},
        {"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "principal_amount", "label": _("Principal"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "interest_amount", "label": _("Interest"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "outstanding_balance", "label": _("Outstanding"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND payment_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND payment_date <= %(to_date)s"
        if filters.get("loan_application"):
            conditions += " AND loan_application = %(loan_application)s"
        if filters.get("customer"):
            conditions += " AND customer = %(customer)s"

    data = frappe.db.sql("""
        SELECT
            name, loan_application, customer, payment_date,
            repayment_type, amount, principal_amount, interest_amount,
            outstanding_balance, status
        FROM `tabLoan Repayment`
        WHERE docstatus = 1 {conditions}
        ORDER BY payment_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
