import frappe
from frappe import _
from frappe.utils import today, add_months


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Lead Name"), "fieldname": "lead_name", "fieldtype": "Data", "width": 200},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Source"), "fieldname": "source", "fieldtype": "Data", "width": 120},
        {"label": _("Loan Type"), "fieldname": "loan_type", "fieldtype": "Data", "width": 120},
        {"label": _("Expected Amount"), "fieldname": "expected_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Assigned To"), "fieldname": "assigned_to", "fieldtype": "Data", "width": 150},
        {"label": _("DSA"), "fieldname": "dsa", "fieldtype": "Data", "width": 150},
        {"label": _("Created On"), "fieldname": "creation", "fieldtype": "Date", "width": 120},
        {"label": _("Days Open"), "fieldname": "days_open", "fieldtype": "Int", "width": 100},
        {"label": _("City"), "fieldname": "city", "fieldtype": "Data", "width": 120},
        {"label": _("Converted"), "fieldname": "converted", "fieldtype": "Check", "width": 100},
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT
            l.name as lead_name,
            l.lead_title,
            l.lead_status as status,
            l.lead_source as source,
            l.loan_type,
            l.expected_amount,
            l.assigned_to,
            l.dsa_name,
            l.dsa_name as dsa,
            l.city,
            l.creation,
            DATEDIFF(CURDATE(), l.creation) as days_open,
            l.converted_to_customer as converted
        FROM `tabLead` l
        WHERE 1=1 {conditions}
        ORDER BY l.creation DESC
    """, as_dict=True)

    return data or []


def get_conditions(filters):
    conditions = ""
    
    if not filters:
        return conditions
    
    if filters.get("status"):
        conditions += f" AND l.lead_status = '{frappe.db.escape(filters['status'])}'"
    
    if filters.get("source"):
        conditions += f" AND l.lead_source = '{frappe.db.escape(filters['source'])}'"
    
    if filters.get("from_date"):
        conditions += f" AND l.creation >= '{filters['from_date']}'"
    
    if filters.get("to_date"):
        conditions += f" AND l.creation <= '{filters['to_date']}'"
    
    if filters.get("dsa_name"):
        conditions += f" AND l.dsa_name = '{frappe.db.escape(filters['dsa_name'])}'"
    
    if filters.get("assigned_to"):
        conditions += f" AND l.assigned_to = '{frappe.db.escape(filters['assigned_to'])}'"
    
    if filters.get("loan_type"):
        conditions += f" AND l.loan_type = '{frappe.db.escape(filters['loan_type'])}'"
    
    return conditions
