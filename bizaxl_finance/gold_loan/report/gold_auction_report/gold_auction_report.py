import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Auction ID"), "fieldname": "name", "fieldtype": "Link", "options": "Gold Auction", "width": 150},
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Pledge"), "fieldname": "pledge", "fieldtype": "Link", "options": "Gold Pledge", "width": 150},
        {"label": _("Auction Date"), "fieldname": "auction_date", "fieldtype": "Date", "width": 100},
        {"label": _("Auction Type"), "fieldname": "auction_type", "fieldtype": "Data", "width": 130},
        {"label": _("Auctioneer"), "fieldname": "auctioneer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Reserve Price"), "fieldname": "reserve_price", "fieldtype": "Currency", "width": 120},
        {"label": _("Final Bid"), "fieldname": "final_bid_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Proceeds"), "fieldname": "auction_proceeds", "fieldtype": "Currency", "width": 120},
        {"label": _("Outstanding Recovered"), "fieldname": "outstanding_recovered", "fieldtype": "Currency", "width": 130},
        {"label": _("Surplus Returned"), "fieldname": "surplus_returned", "fieldtype": "Currency", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND auction_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND auction_date <= %(to_date)s"
        if filters.get("auction_type"):
            conditions += " AND auction_type = %(auction_type)s"
        if filters.get("status"):
            conditions += " AND status = %(status)s"

    data = frappe.db.sql("""
        SELECT name, customer_name, pledge, auction_date, auction_type,
               auctioneer_name, reserve_price, final_bid_amount,
               auction_proceeds, outstanding_recovered, surplus_returned, status
        FROM `tabGold Auction`
        WHERE docstatus < 2 {conditions}
        ORDER BY auction_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
