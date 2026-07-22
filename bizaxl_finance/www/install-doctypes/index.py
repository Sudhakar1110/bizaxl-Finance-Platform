import frappe
from frappe import _

def get_context(context):
    """Load context for the install-doctypes page."""
    # Only System Managers can access this page
    if "System Manager" not in frappe.get_roles():
        frappe.throw(
            _("You need System Manager privileges to access this page."),
            frappe.PermissionError
        )
    
    context.title = "Install DocTypes — Bizaxl Finance"
    context.no_cache = 1
