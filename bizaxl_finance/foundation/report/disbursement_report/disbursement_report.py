import frappe
from frappe import _
def execute(filters=None):
    columns = [
        {"label": _("Applicant"), "fieldname": "applicant_name", "fieldtype": "Data", "width": 180},
        {"label": _("Category"), "fieldname": "loan_category", "fieldtype": "Data", "width": 120},
        {"label": _("Loan Amount"), "fieldname": "loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Disbursed"), "fieldname": "disbursed_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Date"), "fieldname": "disbursement_date", "fieldtype": "Date", "width": 120},
        {"label": _("Mode"), "fieldname": "disbursement_mode", "fieldtype": "Data", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.db.sql("""SELECT applicant_name, loan_category, loan_amount, disbursed_amount,
        disbursement_date, disbursement_mode, status FROM `tabNBFC Loan Application`
        WHERE docstatus < 2 AND disbursement_date IS NOT NULL ORDER BY disbursement_date DESC""", as_dict=True)
    return columns, data