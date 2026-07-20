import frappe

def get_bank_account_permission_query_conditions(user=None):
    """Add query conditions for Bank Account based on user role"""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Customers can only see their own bank accounts
    if "Customer" in user_roles and "System Manager" not in user_roles:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": user}, "name")
        if customer:
            return f"`tabBank Account`.customer = '{customer}'"
        return "1=0"

    return ""


def get_transaction_permission_query_conditions(user=None):
    """Add query conditions for Transaction based on user role"""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if "Customer" in user_roles and "System Manager" not in user_roles:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": user}, "name")
        if customer:
            return f"`tabTransaction`.customer = '{customer}'"
        return "1=0"

    return ""


def get_loan_permission_query_conditions(user=None):
    """Add query conditions for Loan Application based on user role"""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if "Customer" in user_roles and "System Manager" not in user_roles:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": user}, "name")
        if customer:
            return f"`tabLoan Application`.customer = '{customer}'"
        return "1=0"

    return ""


def get_insurance_permission_query_conditions(user=None):
    """Add query conditions for Insurance Policy based on user role"""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if "Customer" in user_roles and "System Manager" not in user_roles:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": user}, "name")
        if customer:
            return f"`tabInsurance Policy`.customer = '{customer}'"
        return "1=0"

    return ""


def has_bank_account_permission(doc, ptype, user=None):
    """Check if user has permission for a specific Bank Account"""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if "System Manager" in user_roles:
        return True

    if "Customer" in user_roles:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": user}, "name")
        if customer == doc.customer:
            return True
        return False

    return True


def has_transaction_permission(doc, ptype, user=None):
    """Check if user has permission for a specific Transaction"""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if "System Manager" in user_roles:
        return True

    if "Customer" in user_roles:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": user}, "name")
        if customer == doc.customer:
            return True
        return False

    return True
