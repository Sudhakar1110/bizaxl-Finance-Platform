import frappe

def execute():
    """Initialize Banking Settings if not exists"""
    if not frappe.db.exists("Banking Settings", "Banking Settings"):
        settings = frappe.get_doc({
            "doctype": "Banking Settings",
            "company_name": "Bizaxl Finance",
            "default_currency": "INR",
            "enable_upi": 1,
            "enable_netbanking": 1,
            "max_upi_daily": 100000,
            "max_upi_per_transaction": 10000,
            "interest_rate_savings": 3.5,
            "interest_rate_fd": 7.0,
        })
        settings.insert(ignore_permissions=True)
