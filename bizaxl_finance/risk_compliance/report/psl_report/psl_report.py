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
        {"label": _("Loan Type"), "fieldname": "loan_type", "fieldtype": "Data", "width": 120},
        {"label": _("Purpose"), "fieldname": "purpose", "fieldtype": "Data", "width": 200},
        {"label": _("Customer Category"), "fieldname": "customer_category", "fieldtype": "Data", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Application Date"), "fieldname": "application_date", "fieldtype": "Date", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    filter_params = {}
    if filters:
        if filters.get("from_date"):
            conditions += " AND application_date >= %(from_date)s"
            filter_params["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            conditions += " AND application_date <= %(to_date)s"
            filter_params["to_date"] = filters["to_date"]
        if filters.get("loan_type"):
            conditions += " AND loan_type = %(loan_type)s"
            filter_params["loan_type"] = filters["loan_type"]

    # Priority Sector Lending: Agriculture, MSME, Education, Housing below threshold
    priority_purposes = [
        "Agriculture", "Farming", "Crop Loan", "MSME", "Small Business",
        "Working Capital", "Education", "Home Loan", "Solar", "Renewable Energy"
    ]

    # Build named parameters for priority purposes
    purpose_params = {}
    purpose_placeholders = []
    for i, purpose in enumerate(priority_purposes):
        key = f"purpose_{i}"
        purpose_params[key] = purpose
        purpose_placeholders.append(f"%({key})s")

    # Merge filter params with purpose params
    query_params = {**filter_params, **purpose_params}

    data = frappe.db.sql(f"""
        SELECT customer_name, name, loan_amount, loan_type, purpose,
               '' as customer_category, status, application_date
        FROM `tabLoan Application`
        WHERE docstatus < 2
        AND (
            loan_type IN ('Agriculture', 'MSME', 'Education')
            OR (loan_type = 'Home Loan' AND loan_amount <= 3500000)
            OR purpose IN ({', '.join(purpose_placeholders)})
        )
        {conditions}
        ORDER BY application_date DESC
    """, query_params, as_dict=1)
    return data
