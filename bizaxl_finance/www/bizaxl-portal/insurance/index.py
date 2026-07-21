import frappe

def get_context(context):
    customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        context.policies = []
        return
    
    context.policies = frappe.db.sql("""
        SELECT name, policy_number, insurance_plan, sum_assured, premium_amount,
               premium_frequency, policy_end_date, status
        FROM `tabInsurance Policy`
        WHERE customer = %s
        ORDER BY creation DESC
    """, customer, as_dict=True)
