import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Chit Group"), "fieldname": "chit_name", "fieldtype": "Data", "width": 150},
        {"label": _("Chit Value"), "fieldname": "chit_value", "fieldtype": "Currency", "width": 120},
        {"label": _("Members"), "fieldname": "number_of_members", "fieldtype": "Int", "width": 80},
        {"label": _("Monthly Subscription"), "fieldname": "monthly_subscription", "fieldtype": "Currency", "width": 120},
        {"label": _("Duration (Months)"), "fieldname": "duration_months", "fieldtype": "Int", "width": 100},
        {"label": _("Foreman"), "fieldname": "foreman_name", "fieldtype": "Data", "width": 150},
        {"label": _("Foreman Commission"), "fieldname": "foreman_commission_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Total Collections"), "fieldname": "total_subscriptions", "fieldtype": "Currency", "width": 130},
        {"label": _("Total Dividends"), "fieldname": "total_dividends", "fieldtype": "Currency", "width": 130},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("status"):
            conditions += " AND status = %(status)s"
        if filters.get("from_date"):
            conditions += " AND start_date >= %(from_date)s"

    data = frappe.db.sql("""
        SELECT
            cg.chit_name, cg.chit_value, cg.number_of_members,
            cg.monthly_subscription, cg.duration_months,
            cg.foreman_name, cg.foreman_commission_amount,
            COALESCE(
                (SELECT SUM(cs.total_subscriptions_paid) FROM `tabChit Subscriber` cs WHERE cs.chit_group = cg.name),
                0
            ) as total_subscriptions,
            COALESCE(
                (SELECT SUM(cs.total_dividend_received) FROM `tabChit Subscriber` cs WHERE cs.chit_group = cg.name),
                0
            ) as total_dividends,
            cg.start_date, cg.status
        FROM `tabChit Group` cg
        WHERE cg.docstatus < 2 {conditions}
        ORDER BY cg.start_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
