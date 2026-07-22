import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "decision_date", "fieldtype": "Date", "width": 100},
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Loan Application"), "fieldname": "loan_application", "fieldtype": "Link", "options": "Loan Application", "width": 150},
        {"label": _("Applied Amount"), "fieldname": "loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Committee Level"), "fieldname": "committee_level", "fieldtype": "Data", "width": 150},
        {"label": _("Decision"), "fieldname": "decision", "fieldtype": "Data", "width": 120},
        {"label": _("Sanctioned Amount"), "fieldname": "sanctioned_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Sanctioned Rate"), "fieldname": "sanctioned_rate", "fieldtype": "Percent", "width": 80},
        {"label": _("Sanctioned Tenure"), "fieldname": "sanctioned_tenure", "fieldtype": "Int", "width": 80},
        {"label": _("Conditions"), "fieldname": "conditions", "fieldtype": "Data", "width": 200},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND decision_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND decision_date <= %(to_date)s"
        if filters.get("committee_level"):
            conditions += " AND committee_level = %(committee_level)s"
        if filters.get("decision"):
            conditions += " AND decision = %(decision)s"

    data = frappe.db.sql("""
        SELECT decision_date, customer_name, loan_application, loan_amount,
               committee_level, decision, sanctioned_amount, sanctioned_rate,
               sanctioned_tenure, conditions, remarks
        FROM `tabCredit Committee Decision`
        WHERE docstatus < 2 {conditions}
        ORDER BY decision_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return columns, data
