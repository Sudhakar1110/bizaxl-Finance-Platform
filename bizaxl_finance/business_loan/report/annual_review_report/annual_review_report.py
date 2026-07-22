import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Business"), "fieldname": "business_name", "fieldtype": "Data", "width": 180},
        {"label": _("Annual Turnover"), "fieldname": "annual_turnover", "fieldtype": "Currency", "width": 120},
        {"label": _("Net Profit"), "fieldname": "net_profit_last_year", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Assets"), "fieldname": "total_assets", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Liabilities"), "fieldname": "total_liabilities", "fieldtype": "Currency", "width": 120},
        {"label": _("DSCR"), "fieldname": "dscr_value", "fieldtype": "Float", "width": 80},
        {"label": _("Existing Borrowings"), "fieldname": "existing_bank_borrowings", "fieldtype": "Currency", "width": 120},
        {"label": _("Vintage (Years)"), "fieldname": "business_vintage_years", "fieldtype": "Int", "width": 80},
        {"label": _("Industry"), "fieldname": "industry", "fieldtype": "Data", "width": 120},
        {"label": _("GSTIN"), "fieldname": "gstin", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND creation >= %(from_date)s"
        if filters.get("industry"):
            conditions += " AND industry = %(industry)s"
        if filters.get("min_turnover"):
            conditions += " AND annual_turnover >= %(min_turnover)s"

    data = frappe.db.sql("""
        SELECT business_name, annual_turnover, net_profit_last_year,
               total_assets, total_liabilities, dscr_value,
               existing_bank_borrowings, business_vintage_years,
               industry, gstin
        FROM `tabBusiness Profile`
        WHERE docstatus < 2 {conditions}
        ORDER BY annual_turnover DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
