import frappe

def get_context(context):
    customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        context.bank_accounts = []
        context.upi_ids = []
        return
    
    context.bank_accounts = frappe.db.sql("""
        SELECT name, bank_name, account_type, account_number, current_balance, status
        FROM `tabBank Account` WHERE customer = %s ORDER BY is_primary DESC
    """, customer, as_dict=True)
    
    context.upi_ids = frappe.db.get_all("UPI ID", {
        "customer": customer
    }, ["upi_id", "bank_name", "is_primary"])
