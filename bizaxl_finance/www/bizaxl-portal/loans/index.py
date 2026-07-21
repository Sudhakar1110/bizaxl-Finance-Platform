import frappe

def get_context(context):
    customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        context.loans = []
        return
    
    loans = frappe.db.sql("""
        SELECT name, loan_product, loan_amount, status, disbursement_date,
               tenure_months, interest_rate, emi_amount,
               (loan_amount - COALESCE((SELECT SUM(amount) FROM `tabLoan Repayment`
                WHERE loan_application = la.name AND docstatus = 1), 0)) as outstanding
        FROM `tabLoan Application` la
        WHERE customer = %s
        ORDER BY creation DESC
    """, customer, as_dict=True)
    
    status_colors = {
        "Draft": "secondary", "Under Review": "warning", "Approved": "info",
        "Disbursed": "success", "Closed": "dark", "Defaulted": "danger", "Rejected": "danger"
    }
    for loan in loans:
        loan.status_color = status_colors.get(loan.status, "secondary")
    
    context.loans = loans
