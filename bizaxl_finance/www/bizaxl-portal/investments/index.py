import frappe

def get_context(context):
    customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        context.holdings = []
        context.mutual_funds = []
        context.fixed_deposits = []
        context.digital_gold = []
        return
    
    context.holdings = frappe.db.sql("""
        SELECT asset_type, invested_amount, current_value,
               ROUND((current_value - invested_amount) / invested_amount * 100, 2) as return_pct
        FROM `tabPortfolio Holding`
        WHERE customer = %s AND status = 'Active'
    """, customer, as_dict=True)
    
    context.mutual_funds = frappe.db.get_all("Mutual Fund",
        {"customer": customer, "status": "Active"},
        ["name", "fund_name", "folio_number", "invested_amount", "current_value", "fund_type"]
    )
    
    context.fixed_deposits = frappe.db.get_all("Fixed Deposit",
        {"customer": customer, "status": "Active"},
        ["name", "fd_number", "deposit_amount", "maturity_amount", "maturity_date", "interest_rate"]
    )
    
    context.digital_gold = frappe.db.get_all("Digital Gold",
        {"customer": customer, "status": "Active"},
        ["name", "gold_grams", "purchase_rate", "current_value"]
    )
