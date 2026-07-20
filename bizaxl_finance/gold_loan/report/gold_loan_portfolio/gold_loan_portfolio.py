import frappe
from frappe import _
def execute(filters=None):
    columns = [
        {"label": _("Pledge ID"), "fieldname": "name", "fieldtype": "Link", "options": "Gold Pledge", "width": 150},
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Loan Amount"), "fieldname": "loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Gold Value"), "fieldname": "total_gold_value", "fieldtype": "Currency", "width": 120},
        {"label": _("LTV"), "fieldname": "ltv_ratio", "fieldtype": "Percent", "width": 80},
        {"label": _("Interest Rate"), "fieldname": "interest_rate", "fieldtype": "Percent", "width": 80},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Maturity Date"), "fieldname": "maturity_date", "fieldtype": "Date", "width": 120},
    ]
    data = frappe.db.sql("""SELECT name, customer_name, loan_amount, total_gold_value, ltv_ratio,
        interest_rate, status, maturity_date FROM `tabGold Pledge`
        WHERE docstatus < 2 ORDER BY creation DESC""", as_dict=True)
    return columns, data