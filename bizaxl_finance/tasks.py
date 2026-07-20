from __future__ import unicode_literals
import frappe
from frappe.utils import today, now_datetime, add_days, add_months, date_diff

def process_due_premiums():
    """Process due insurance premiums"""
    policies = frappe.db.sql("""
        SELECT ip.name as policy_name, ip.customer, ip.premium_amount, ip.premium_frequency,
               ip.policy_start_date
        FROM `tabInsurance Policy` ip
        WHERE ip.status = 'Active'
    """, as_dict=True)

    for policy in policies:
        # Check if premium is due
        if policy.premium_frequency == "Monthly":
            due_date = add_months(policy.policy_start_date, 1)
        elif policy.premium_frequency == "Quarterly":
            due_date = add_months(policy.policy_start_date, 3)
        elif policy.premium_frequency == "Yearly":
            due_date = add_months(policy.policy_start_date, 12)
        else:
            continue

        if due_date <= today():
            existing = frappe.db.exists("Premium Payment", {
                "insurance_policy": policy.policy_name,
                "status": "Pending"
            })
            if not existing:
                premium = frappe.get_doc({
                    "doctype": "Premium Payment",
                    "insurance_policy": policy.policy_name,
                    "customer": policy.customer,
                    "premium_amount": policy.premium_amount,
                    "premium_due_date": due_date,
                    "status": "Pending",
                })
                premium.insert()


def calculate_loan_interest():
    """Calculate and update loan interest"""
    loans = frappe.db.sql("""
        SELECT name, loan_amount, interest_rate, tenure_months
        FROM `tabLoan Application`
        WHERE status = 'Disbursed'
    """, as_dict=True)

    for loan in loans:
        # Update outstanding balance calculation
        total_paid = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0)
            FROM `tabLoan Repayment`
            WHERE loan_application = %s AND docstatus = 1
        """, loan.name)[0][0]

        outstanding = loan.loan_amount - total_paid
        if outstanding <= 0:
            frappe.db.set_value("Loan Application", loan.name, "status", "Closed")


def update_credit_scores():
    """Update customer credit scores based on activity"""
    customers = frappe.db.sql("""
        SELECT bc.name, bc.credit_score
        FROM `tabBizaxl Customer` bc
        WHERE bc.is_active = 1
    """, as_dict=True)

    for customer in customers:
        # Calculate score impact based on:
        # 1. On-time loan repayments
        # 2. Average bank balance
        # 3. Transaction regularity

        late_payments = frappe.db.sql("""
            SELECT COUNT(*) as late_count
            FROM `tabLoan Repayment` lr
            INNER JOIN `tabLoan Application` la ON lr.loan_application = la.name
            WHERE la.customer = %s AND lr.docstatus = 1
                AND lr.payment_date > la.first_emi_date
        """, customer.name)[0][0]

        avg_balance = frappe.db.sql("""
            SELECT COALESCE(AVG(current_balance), 0)
            FROM `tabBank Account`
            WHERE customer = %s AND status = 'Active'
        """, customer.name)[0][0]

        # Simple scoring logic
        new_score = customer.credit_score or 700
        if late_payments > 0:
            new_score -= late_payments * 10
        if avg_balance > 50000:
            new_score += 5
        if avg_balance > 200000:
            new_score += 10

        new_score = max(300, min(900, new_score))

        if new_score != customer.credit_score:
            frappe.db.set_value("Bizaxl Customer", customer.name, "credit_score", new_score)

            # Log score change
            history = frappe.get_doc({
                "doctype": "Credit Score History",
                "customer": customer.name,
                "credit_score": new_score,
                "previous_score": customer.credit_score or 0,
                "change_reason": "Automatic monthly update",
            })
            history.insert(ignore_permissions=True)


def process_recurring_bill_payments():
    """Process recurring bill payments"""
    today_date = today()
    recurring_bills = frappe.db.sql("""
        SELECT name, customer, bill_type, provider, amount, due_date, recurring_frequency
        FROM `tabBill Payment`
        WHERE is_recurring = 1 AND status = 'Paid'
    """, as_dict=True)

    for bill in recurring_bills:
        if bill.recurring_frequency == "Monthly":
            new_due = add_months(bill.due_date, 1)
        elif bill.recurring_frequency == "Quarterly":
            new_due = add_months(bill.due_date, 3)
        elif bill.recurring_frequency == "Yearly":
            new_due = add_months(bill.due_date, 12)
        else:
            continue

        if new_due <= today_date:
            new_bill = frappe.get_doc({
                "doctype": "Bill Payment",
                "customer": bill.customer,
                "bill_type": bill.bill_type,
                "provider": bill.provider,
                "amount": bill.amount,
                "due_date": new_due,
                "is_recurring": 1,
                "recurring_frequency": bill.recurring_frequency,
            })
            new_bill.insert()


def send_due_payment_reminders():
    """Send reminders for due payments"""
    three_days_from_now = add_days(today(), 3)

    # Find bills due in 3 days
    bills_due = frappe.db.sql("""
        SELECT bp.name, bp.customer, bp.bill_type, bp.provider, bp.amount,
               bp.due_date, bc.customer_name
        FROM `tabBill Payment` bp
        INNER JOIN `tabBizaxl Customer` bc ON bc.name = bp.customer
        WHERE bp.status = 'Pending' AND bp.due_date = %s
    """, three_days_from_now, as_dict=True)

    for bill in bills_due:
        # Create notification
        notification = frappe.get_doc({
            "doctype": "Customer Communication",
            "customer": bill.customer,
            "subject": f"Payment Reminder: {bill.bill_type} bill due",
            "message_body": f"Dear {bill.customer_name}, your {bill.bill_type} bill of ₹{bill.amount:,.2f} is due on {bill.due_date}. Please pay before the due date to avoid late fees.",
            "channel": "App Notification",
            "communication_type": "Reminder",
            "status": "Sent",
        })
        notification.insert(ignore_permissions=True)

    # Check for overdue bills
    overdue_bills = frappe.db.sql("""
        SELECT name FROM `tabBill Payment`
        WHERE status = 'Pending' AND due_date < %s
    """, today(), as_dict=True)

    for bill in overdue_bills:
        frappe.db.set_value("Bill Payment", bill.name, "status", "Overdue")


def generate_portfolio_summaries():
    """Generate weekly portfolio summaries for all customers"""
    customers = frappe.db.get_all("Bizaxl Customer", filters={"is_active": 1}, pluck="name")

    for customer in customers:
        summary = frappe.get_doc({
            "doctype": "Portfolio Summary",
            "customer": customer,
        })
        summary.insert(ignore_permissions=True)


def generate_customer_statements():
    """Generate customer transaction statements"""
    customers = frappe.db.get_all("Bizaxl Customer", filters={"is_active": 1}, pluck="name")

    for customer in customers:
        transactions = frappe.db.sql("""
            SELECT transaction_date, transaction_type, amount, description, status
            FROM `tabTransaction`
            WHERE customer = %s AND docstatus = 1
                AND DATE(transaction_date) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            ORDER BY transaction_date DESC
        """, customer, as_dict=True)

        if transactions:
            customer_doc = frappe.get_doc("Bizaxl Customer", customer)
            # Generate statement communication
            statement = frappe.get_doc({
                "doctype": "Customer Communication",
                "customer": customer,
                "subject": "Your Weekly Transaction Statement",
                "message_body": f"Dear {customer_doc.customer_name}, here's your weekly transaction summary. Total transactions: {len(transactions)}",
                "channel": "App Notification",
                "communication_type": "Transaction",
                "status": "Sent",
            })
            statement.insert(ignore_permissions=True)


def generate_maturity_alerts():
    """Generate alerts for maturing investments"""
    # Fixed deposits maturing in 30 days
    upcoming_fd = frappe.db.sql("""
        SELECT fd.name, fd.customer, fd.fd_number, fd.deposit_amount, fd.maturity_amount,
               fd.maturity_date, bc.customer_name
        FROM `tabFixed Deposit` fd
        INNER JOIN `tabBizaxl Customer` bc ON bc.name = fd.customer
        WHERE fd.status = 'Active'
            AND fd.maturity_date BETWEEN %s AND DATE_ADD(%s, INTERVAL 30 DAY)
    """, (today(), today()), as_dict=True)

    for fd in upcoming_fd:
        notification = frappe.get_doc({
            "doctype": "Customer Communication",
            "customer": fd.customer,
            "subject": f"FD Maturity Alert: {fd.fd_number}",
            "message_body": f"Dear {fd.customer_name}, your Fixed Deposit {fd.fd_number} of ₹{fd.deposit_amount:,.2f} is maturing on {fd.maturity_date}. Maturity amount: ₹{fd.maturity_amount:,.2f}.",
            "channel": "App Notification",
            "communication_type": "Alert",
            "status": "Sent",
        })
        notification.insert(ignore_permissions=True)

    # Insurance policies maturing in 30 days
    upcoming_policies = frappe.db.sql("""
        SELECT ip.name, ip.customer, ip.policy_number, ip.sum_assured,
               ip.policy_end_date, bc.customer_name
        FROM `tabInsurance Policy` ip
        INNER JOIN `tabBizaxl Customer` bc ON bc.name = ip.customer
        WHERE ip.status = 'Active'
            AND ip.policy_end_date BETWEEN %s AND DATE_ADD(%s, INTERVAL 30 DAY)
    """, (today(), today()), as_dict=True)

    for policy in upcoming_policies:
        notification = frappe.get_doc({
            "doctype": "Customer Communication",
            "customer": policy.customer,
            "subject": f"Policy Maturity Alert: {policy.policy_number}",
            "message_body": f"Dear {policy.customer_name}, your insurance policy {policy.policy_number} with sum assured ₹{policy.sum_assured:,.2f} is maturing on {policy.policy_end_date}.",
            "channel": "App Notification",
            "communication_type": "Alert",
            "status": "Sent",
        })
        notification.insert(ignore_permissions=True)


def calculate_commission_payouts():
    """Calculate commission payouts (placeholder for partner/agent commissions)"""
    # Placeholder for future implementation
    pass
