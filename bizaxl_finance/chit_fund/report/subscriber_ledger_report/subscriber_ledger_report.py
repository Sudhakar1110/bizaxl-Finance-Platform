import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Chit Group"), "fieldname": "chit_group_name", "fieldtype": "Data", "width": 150},
        {"label": _("Subscriber #"), "fieldname": "subscriber_number", "fieldtype": "Int", "width": 80},
        {"label": _("Subscriber"), "fieldname": "subscriber_name", "fieldtype": "Data", "width": 180},
        {"label": _("Type"), "fieldname": "subscriber_type", "fieldtype": "Data", "width": 80},
        {"label": _("Total Paid"), "fieldname": "total_subscriptions_paid", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Dividend"), "fieldname": "total_dividend_received", "fieldtype": "Currency", "width": 120},
        {"label": _("Prize Amount"), "fieldname": "prize_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Prized Date"), "fieldname": "prized_date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("chit_group"):
            conditions += " AND chit_group = %(chit_group)s"
        if filters.get("status"):
            conditions += " AND status = %(status)s"
        if filters.get("subscriber_type"):
            conditions += " AND subscriber_type = %(subscriber_type)s"

    data = frappe.db.sql("""
        SELECT
            cs.chit_group,
            (SELECT cg.chit_name FROM `tabChit Group` cg WHERE cg.name = cs.chit_group) as chit_group_name,
            cs.subscriber_number, cs.subscriber_name, cs.subscriber_type,
            cs.total_subscriptions_paid, cs.total_dividend_received,
            cs.prize_amount, cs.prized_date, cs.status
        FROM `tabChit Subscriber` cs
        WHERE cs.docstatus < 2 {conditions}
        ORDER BY cs.chit_group, cs.subscriber_number
    """.format(conditions=conditions), filters, as_dict=1)
    return data
