import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Metric"), "fieldname": "metric", "fieldtype": "Data", "width": 250},
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Data", "width": 150},
        {"label": _("As of Date"), "fieldname": "as_of_date", "fieldtype": "Date", "width": 100},
    ]

def get_data(filters):
    today = frappe.utils.today()

    # Portfolio metrics
    total_outstanding = frappe.db.sql("""
        SELECT COALESCE(SUM(COALESCE(total_outstanding, 0)), 0) 
        FROM `tabMFI Member` WHERE status = 'Active' AND docstatus < 2
    """)[0][0]

    total_members = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabMFI Member` WHERE status = 'Active' AND docstatus < 2
    """)[0][0]

    total_centers = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabMFI Center` WHERE status = 'Active' AND docstatus < 2
    """)[0][0]

    total_groups = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabJLG Group` WHERE status = 'Active' AND docstatus < 2
    """)[0][0]

    par_30 = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabMFI Member` 
        WHERE overdue_days >= 30 AND status = 'Active' AND docstatus < 2
    """)[0][0]

    par_60 = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabMFI Member` 
        WHERE overdue_days >= 60 AND status = 'Active' AND docstatus < 2
    """)[0][0]

    par_90 = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabMFI Member` 
        WHERE overdue_days >= 90 AND status = 'Active' AND docstatus < 2
    """)[0][0]

    # Active loan cycles
    active_cycles = frappe.db.sql("""
        SELECT COALESCE(AVG(current_cycle), 0) FROM `tabJLG Group` 
        WHERE status = 'Active' AND docstatus < 2
    """)[0][0]

    data = [
        {"metric": "Total Portfolio Outstanding", "value": f"Rs. {total_outstanding:,.2f}", "as_of_date": today},
        {"metric": "Active Members", "value": str(total_members), "as_of_date": today},
        {"metric": "Active Centers", "value": str(total_centers), "as_of_date": today},
        {"metric": "Active JLG/SHG Groups", "value": str(total_groups), "as_of_date": today},
        {"metric": "PAR 30+ (Members)", "value": str(par_30), "as_of_date": today},
        {"metric": "PAR 60+ (Members)", "value": str(par_60), "as_of_date": today},
        {"metric": "PAR 90+ (Members)", "value": str(par_90), "as_of_date": today},
        {"metric": "Average Loan Cycle", "value": f"{active_cycles:.1f}", "as_of_date": today},
        {"metric": "Average Outstanding per Member", "value": f"Rs. {total_outstanding / max(total_members, 1):,.2f}", "as_of_date": today},
        {"metric": "Members per Center (Avg)", "value": f"{total_members / max(total_centers, 1):.1f}", "as_of_date": today},
    ]
    return columns, data
