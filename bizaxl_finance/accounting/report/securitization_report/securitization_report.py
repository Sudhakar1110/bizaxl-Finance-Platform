import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Loan Accounting"), "fieldname": "name", "fieldtype": "Link", "options": "Loan Accounting", "width": 150},
        {"label": _("Loan Application"), "fieldname": "loan_application", "fieldtype": "Link", "options": "Loan Application", "width": 150},
        {"label": _("Transaction Type"), "fieldname": "transaction_type", "fieldtype": "Data", "width": 130},
        {"label": _("Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Debit Account"), "fieldname": "account_debit", "fieldtype": "Data", "width": 150},
        {"label": _("Credit Account"), "fieldname": "account_credit", "fieldtype": "Data", "width": 150},
        {"label": _("GL Reference"), "fieldname": "gl_entry_reference", "fieldtype": "Data", "width": 150},
    ]

def get_data(filters):
    conditions = ""
    if filters:
        if filters.get("from_date"):
            conditions += " AND transaction_date >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " AND transaction_date <= %(to_date)s"

    # Securitization: Fund Account type = 'Securitization Pool' + related Loan Accounting entries
    data = frappe.db.sql("""
        SELECT la.name, la.loan_application, la.transaction_type,
               la.transaction_date, la.amount, la.account_debit,
               la.account_credit, la.gl_entry_reference
        FROM `tabLoan Accounting` la
        WHERE la.docstatus < 2
        AND la.transaction_type IN ('Disbursement', 'Repayment', 'Write-off')
        AND EXISTS (
            SELECT 1 FROM `tabFund Account` fa
            WHERE fa.fund_type = 'Securitization Pool'
            AND fa.is_active = 1
        )
        {conditions}
        ORDER BY la.transaction_date DESC
    """.format(conditions=conditions), filters, as_dict=1)
    return data
