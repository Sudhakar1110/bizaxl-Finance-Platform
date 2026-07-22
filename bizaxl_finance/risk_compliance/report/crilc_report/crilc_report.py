import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Loan Application"), "fieldname": "loan_application", "fieldtype": "Link", "options": "Loan Application", "width": 150},
        {"label": _("Loan Amount"), "fieldname": "loan_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Outstanding"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Asset Classification"), "fieldname": "asset_classification", "fieldtype": "Data", "width": 150},
        {"label": _("NPA Category"), "fieldname": "npa_category", "fieldtype": "Data", "width": 120},
        {"label": _("DPD Days"), "fieldname": "dpd_days", "fieldtype": "Int", "width": 80},
        {"label": _("Provision %"), "fieldname": "provision_percentage", "fieldtype": "Percent", "width": 80},
        {"label": _("Provision Amount"), "fieldname": "provision_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Classification Date"), "fieldname": "classification_date", "fieldtype": "Date", "width": 120},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND classification_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND classification_date <= %(to_date)s"

    # CRILC: exposures >= Rs.5Cr
    data = frappe.db.sql("""
        SELECT
            npa.customer_name, npa.loan_application, npa.outstanding_amount,
            npa.dpd_days, npa.asset_classification, npa.npa_category,
            npa.provision_percentage, npa.provision_amount, npa.classification_date
        FROM `tabNPA Classification` npa
        INNER JOIN `tabLoan Application` la ON la.name = npa.loan_application
        WHERE npa.outstanding_amount >= 50000000
        AND npa.docstatus < 2
        {conditions}
        ORDER BY npa.outstanding_amount DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
