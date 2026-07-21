import frappe

def get_context(context):
    customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        context.bills = []
        return
    
    context.bills = frappe.db.sql("""
        SELECT name, bill_type, provider, amount, due_date, status
        FROM `tabBill Payment`
        WHERE customer = %s
        ORDER BY due_date ASC
    """, customer, as_dict=True)
    
    context.upi_ids = frappe.db.get_all("UPI ID", {"customer": customer}, ["upi_id"])
