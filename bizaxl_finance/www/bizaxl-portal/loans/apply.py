import frappe

def get_context(context):
    context.loan_products = frappe.db.get_all("Loan Product",
        {"is_active": 1},
        ["name", "loan_type", "minimum_amount", "maximum_amount", "interest_rate", "tenure_months"]
    )

@frappe.whitelist(allow_guest=False)
def submit_loan_application(**kwargs):
    """Process loan application from portal form"""
    customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return {"error": "Customer profile not found"}
    
    loan = frappe.get_doc({
        "doctype": "Loan Application",
        "customer": customer,
        "loan_product": kwargs.get("loan_product"),
        "loan_amount": frappe.utils.flt(kwargs.get("loan_amount")),
        "tenure_months": int(kwargs.get("tenure_months", 12)),
        "interest_rate": frappe.utils.flt(kwargs.get("interest_rate")),
        "purpose": kwargs.get("purpose"),
        "status": "Draft",
    })
    loan.insert(ignore_permissions=True)
    
    # Create notification
    frappe.get_doc({
        "doctype": "Customer Communication",
        "customer": customer,
        "subject": "Loan Application Submitted",
        "message_body": f"Your loan application for ₹{loan.loan_amount:,.2f} has been submitted successfully.",
        "channel": "App Notification",
        "communication_type": "Notification",
        "status": "Sent",
    }).insert(ignore_permissions=True)
    
    return {"success": True, "loan_id": loan.name}
