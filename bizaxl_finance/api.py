import frappe
from frappe import _
import json

# ── Customer Portal APIs ──────────────────────────────────────────────────

@frappe.whitelist()
def get_customer_dashboard(customer=None):
    """Get customer dashboard data"""
    if not customer:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return {}

    customer_doc = frappe.get_doc("Bizaxl Customer", customer)
    return customer_doc.get_dashboard_data()


@frappe.whitelist()
def get_recent_transactions(customer=None, limit=10):
    """Get recent transactions for a customer"""
    if not customer:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return []

    return frappe.db.sql("""
        SELECT name, transaction_date, transaction_type, amount, description, status
        FROM `tabTransaction`
        WHERE customer = %s AND docstatus = 1
        ORDER BY transaction_date DESC
        LIMIT %s
    """, (customer, limit), as_dict=True)


@frappe.whitelist()
def get_portfolio_summary(customer=None):
    """Get portfolio summary for a customer"""
    if not customer:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return {}

    holdings = frappe.db.sql("""
        SELECT asset_type, 
               COALESCE(SUM(invested_amount), 0) as total_invested,
               COALESCE(SUM(current_value), 0) as total_current
        FROM `tabPortfolio Holding`
        WHERE customer = %s AND status = 'Active'
        GROUP BY asset_type
    """, customer, as_dict=True)

    mutual_funds = frappe.db.sql("""
        SELECT COUNT(*) as count, COALESCE(SUM(current_value), 0) as value
        FROM `tabMutual Fund`
        WHERE customer = %s AND status = 'Active'
    """, customer, as_dict=True)

    fixed_deposits = frappe.db.sql("""
        SELECT COUNT(*) as count, COALESCE(SUM(deposit_amount), 0) as value
        FROM `tabFixed Deposit`
        WHERE customer = %s AND status = 'Active'
    """, customer, as_dict=True)

    digital_gold = frappe.db.sql("""
        SELECT COALESCE(SUM(gold_grams), 0) as total_grams,
               COALESCE(SUM(current_value), 0) as value
        FROM `tabDigital Gold`
        WHERE customer = %s AND status = 'Active'
    """, customer, as_dict=True)

    return {
        "holdings": holdings,
        "mutual_funds": mutual_funds[0] if mutual_funds else {},
        "fixed_deposits": fixed_deposits[0] if fixed_deposits else {},
        "digital_gold": digital_gold[0] if digital_gold else {},
    }


@frappe.whitelist()
def get_loan_summary(customer=None):
    """Get loan summary for a customer"""
    if not customer:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return {}

    active_loans = frappe.db.sql("""
        SELECT COUNT(*) as count, COALESCE(SUM(loan_amount), 0) as total_amount
        FROM `tabLoan Application`
        WHERE customer = %s AND status IN ('Disbursed', 'Approved')
    """, customer, as_dict=True)

    total_outstanding = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0) as outstanding
        FROM `tabLoan Repayment`
        WHERE customer = %s AND docstatus = 1
    """, customer, as_dict=True)

    return {
        "active_loans": active_loans[0] if active_loans else {},
        "total_outstanding": total_outstanding[0] if total_outstanding else {},
    }


@frappe.whitelist()
def get_insurance_summary(customer=None):
    """Get insurance summary for a customer"""
    if not customer:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return {}

    active_policies = frappe.db.sql("""
        SELECT COUNT(*) as count, COALESCE(SUM(sum_assured), 0) as total_coverage
        FROM `tabInsurance Policy`
        WHERE customer = %s AND status = 'Active'
    """, customer, as_dict=True)

    pending_premiums = frappe.db.sql("""
        SELECT COUNT(*) as count, COALESCE(SUM(premium_amount), 0) as total_due
        FROM `tabPremium Payment`
        WHERE customer = %s AND status = 'Pending'
    """, customer, as_dict=True)

    return {
        "active_policies": active_policies[0] if active_policies else {},
        "pending_premiums": pending_premiums[0] if pending_premiums else {},
    }


@frappe.whitelist()
def get_upcoming_bills(customer=None, days=30):
    """Get upcoming bill payments for a customer"""
    if not customer:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return []

    return frappe.db.sql("""
        SELECT name, bill_type, provider, amount, due_date, status
        FROM `tabBill Payment`
        WHERE customer = %s AND status = 'Pending'
        ORDER BY due_date ASC
        LIMIT 10
    """, customer, as_dict=True)


@frappe.whitelist()
def get_credit_report(customer=None):
    """Get credit report for a customer"""
    if not customer:
        customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return {}

    credit_report = frappe.db.sql("""
        SELECT credit_score, report_date, bureau_name, score_range
        FROM `tabCredit Report`
        WHERE customer = %s
        ORDER BY report_date DESC
        LIMIT 1
    """, customer, as_dict=True)

    score_history = frappe.db.sql("""
        SELECT credit_score, changed_on, change_reason
        FROM `tabCredit Score History`
        WHERE customer = %s
        ORDER BY changed_on DESC
        LIMIT 12
    """, customer, as_dict=True)

    return {
        "latest_report": credit_report[0] if credit_report else {},
        "score_history": score_history,
    }


# ── Transaction APIs ──────────────────────────────────────────────────────

@frappe.whitelist()
def initiate_upi_transfer(from_upi, to_upi, amount, description=""):
    """Initiate a UPI transfer"""
    customer = frappe.db.get_value("UPI ID", from_upi, "customer")
    if not customer:
        frappe.throw("Invalid UPI ID")

    # Create transaction
    transaction = frappe.get_doc({
        "doctype": "Transaction",
        "customer": customer,
        "transaction_type": "Debit",
        "transaction_category": "UPI Transfer",
        "amount": amount,
        "from_upi": from_upi,
        "to_upi": to_upi,
        "description": description or f"UPI Transfer to {to_upi}",
        "status": "Completed",
    })
    transaction.insert()
    transaction.submit()

    return transaction.name


@frappe.whitelist()
def initiate_bill_payment(customer, bill_payment_id, payment_method=None):
    """Initiate a bill payment"""
    bill = frappe.get_doc("Bill Payment", bill_payment_id)
    if bill.status != "Pending":
        frappe.throw("Bill payment is not pending")

    bill.payment_method = payment_method
    bill.submit()

    return bill.name


@frappe.whitelist()
def create_loan_repayment(loan_application, amount, repayment_type="Scheduled EMI"):
    """Create a loan repayment"""
    loan = frappe.get_doc("Loan Application", loan_application)
    if loan.status not in ["Disbursed", "Approved"]:
        frappe.throw("Loan is not active")

    repayment = frappe.get_doc({
        "doctype": "Loan Repayment",
        "loan_application": loan_application,
        "customer": loan.customer,
        "amount": amount,
        "repayment_type": repayment_type,
    })
    repayment.insert()
    repayment.submit()

    return repayment.name


# ── Notification APIs ─────────────────────────────────────────────────────

@frappe.whitelist()
def send_notification(customer, subject, message, channel="App Notification"):
    """Send notification to a customer"""
    comm = frappe.get_doc({
        "doctype": "Customer Communication",
        "customer": customer,
        "subject": subject,
        "message_body": message,
        "channel": channel,
        "communication_type": "Notification",
        "status": "Sent",
    })
    comm.insert()
    return comm.name


# ── Admin APIs ────────────────────────────────────────────────────────────

@frappe.whitelist()
def verify_kyc_document(document_id, verification_status, remarks=""):
    """Verify a KYC document"""
    doc = frappe.get_doc("KYC Document", document_id)
    doc.verification_status = verification_status
    doc.remarks = remarks
    doc.save(ignore_permissions=True)

    # Update customer KYC status if all documents verified
    pending_docs = frappe.db.count("KYC Document", {
        "customer": doc.customer,
        "verification_status": ["!=", "Verified"]
    })
    if pending_docs == 0:
        frappe.db.set_value("Bizaxl Customer", doc.customer, "kyc_status", "Verified")
        frappe.db.set_value("Bizaxl Customer", doc.customer, "kyc_verified_on", frappe.utils.today())

    return doc.name


@frappe.whitelist()
def get_customer_statements(customer, from_date, to_date):
    """Get customer transaction statements"""
    return frappe.db.sql("""
        SELECT transaction_date, transaction_type, amount, description,
               balance_before_transaction, balance_after_transaction, status
        FROM `tabTransaction`
        WHERE customer = %s
            AND DATE(transaction_date) BETWEEN %s AND %s
            AND docstatus = 1
        ORDER BY transaction_date ASC
    """, (customer, from_date, to_date), as_dict=True)
