import frappe
from frappe import _


def get_context(context):
    """Load portal dashboard data for the logged-in customer"""
    customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    
    if not customer:
        context.total_balance = 0
        context.active_loans = 0
        context.investment_value = 0
        context.active_policies = 0
        context.recent_transactions = []
        context.upcoming_bills = []
        context.full_name = frappe.session.user
        return
    
    customer_doc = frappe.get_doc("Bizaxl Customer", customer)
    context.full_name = customer_doc.customer_name
    
    # Total balance across all bank accounts
    balance_data = frappe.db.sql("""
        SELECT COALESCE(SUM(current_balance), 0) as total
        FROM `tabBank Account` WHERE customer = %s AND status = 'Active'
    """, customer, as_dict=True)
    context.total_balance = balance_data[0].total if balance_data else 0
    
    # Active loans count
    context.active_loans = frappe.db.count("Loan Application", {
        "customer": customer, "status": ["in", ["Disbursed", "Approved"]]
    })
    
    # Investment portfolio value
    inv_data = frappe.db.sql("""
        SELECT COALESCE(SUM(current_value), 0) as value
        FROM `tabPortfolio Holding` WHERE customer = %s AND status = 'Active'
    """, customer, as_dict=True)
    context.investment_value = inv_data[0].value if inv_data else 0
    
    # Active insurance policies
    context.active_policies = frappe.db.count("Insurance Policy", {
        "customer": customer, "status": "Active"
    })
    
    # Recent transactions (last 5)
    context.recent_transactions = frappe.db.sql("""
        SELECT transaction_date, transaction_type, description, amount, status
        FROM `tabTransaction`
        WHERE customer = %s AND docstatus = 1
        ORDER BY transaction_date DESC LIMIT 5
    """, customer, as_dict=True)
    
    # Upcoming bills
    context.upcoming_bills = frappe.db.sql("""
        SELECT bill_type, provider, amount, due_date
        FROM `tabBill Payment`
        WHERE customer = %s AND status = 'Pending'
        ORDER BY due_date ASC LIMIT 5
    """, customer, as_dict=True)
