import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Applicant"), "fieldname": "applicant_name", "fieldtype": "Data", "width": 180},
        {"label": _("Aadhaar"), "fieldname": "aadhaar", "fieldtype": "Data", "width": 130},
        {"label": _("Income Category"), "fieldname": "income_category", "fieldtype": "Data", "width": 140},
        {"label": _("First Home"), "fieldname": "is_first_home", "fieldtype": "Data", "width": 80},
        {"label": _("Eligible for CLSS"), "fieldname": "eligible_for_clss", "fieldtype": "Data", "width": 100},
        {"label": _("Subsidy Amount"), "fieldname": "subsidy_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Principal Reduction"), "fieldname": "principal_reduction", "fieldtype": "Currency", "width": 130},
        {"label": _("Status"), "fieldname": "subsidy_status", "fieldtype": "Data", "width": 130},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("subsidy_status"):
            conditions += " AND subsidy_status = %(subsidy_status)s"
        if filters.get("income_category"):
            conditions += " AND income_category = %(income_category)s"

    data = frappe.db.sql("""
        SELECT applicant_name, aadhaar, income_category,
               CASE WHEN is_first_home = 1 THEN 'Yes' ELSE 'No' END as is_first_home,
               CASE WHEN eligible_for_clss = 1 THEN 'Yes' ELSE 'No' END as eligible_for_clss,
               subsidy_amount, principal_reduction, subsidy_status
        FROM `tabPMAY Subsidy`
        WHERE docstatus < 2 {conditions}
        ORDER BY subsidy_amount DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return columns, data
