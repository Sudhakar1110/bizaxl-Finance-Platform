"""Bizaxl Finance — Setup & Uninstall Hooks"""

import frappe


def before_uninstall():
    """Change module references on all doctypes before uninstall.
    
    Frappe deletes modules before doctypes during uninstall-app.
    This causes errors when doctypes reference custom modules
    that have already been deleted. This hook reassigns them
    to a built-in module before the uninstall process begins.
    """
    modules_to_fix = frappe.get_all("DocType", 
        filters={"module": ["in", ["Bizaxl Finance", "Foundation", "Banking", "Payments", 
                                   "Investments", "Loans", "Insurance", "Credit Management",
                                   "Portfolio Management", "Customer Management", "NBFC Lending",
                                   "Gold Loan", "Microfinance", "Vehicle Loan", "Home Loan",
                                   "Business Loan", "Education Loan", "BNPL", "Invoice Finance",
                                   "Chit Fund", "Consumer Finance", "Collections", "Risk Compliance",
                                   "Risk & Compliance", "Accounting"]]},
        pluck="name"
    )
    
    for doctype in modules_to_fix:
        frappe.db.set_value("DocType", doctype, "module", "Setup")
    
    frappe.db.commit()
    print(f"✅ Changed module for {len(modules_to_fix)} doctypes to 'Setup'")
