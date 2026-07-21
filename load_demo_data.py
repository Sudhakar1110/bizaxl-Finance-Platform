"""
Demo Data Loader for Bizaxl Finance
Run: bench --site finance.bizaxl.local console
Then paste this entire code
"""

import frappe
import random
from datetime import datetime, timedelta

print("=" * 60)
print("BIZAXL FINANCE - LOADING DEMO DATA")
print("=" * 60)

# Helper function
def create_doc(doctype, data, submit=False):
    try:
        if not frappe.db.exists(doctype, data.get("name")):
            doc = frappe.get_doc({
                "doctype": doctype,
                **{k: v for k, v in data.items() if k != "doctype"}
            })
            doc.insert(ignore_permissions=True)
            if submit and doc.docstatus == 0:
                doc.submit()
            frappe.db.commit()
            return True
    except Exception as e:
        print(f"   Error creating {data.get('name')}: {str(e)[:50]}")
    return False

count = 0

# ============================================
# 1. CUSTOMER MANAGEMENT
# ============================================
print("\n1. Creating Customers...")

customers = [
    {"doctype": "Bizaxl Customer", "name": "CUST-001", "customer_name": "Rajesh Kumar", "customer_type": "Individual", "mobile_no": "9876543210", "email": "rajesh@example.com", "pan": "AAAPL1234C", "date_of_birth": "1985-05-15", "occupation": "Business", "annual_income": 1200000},
    {"doctype": "Bizaxl Customer", "name": "CUST-002", "customer_name": "Priya Sharma", "customer_type": "Individual", "mobile_no": "9876543211", "email": "priya@example.com", "pan": "BBAPL1234C", "date_of_birth": "1990-08-20", "occupation": "Salaried", "annual_income": 800000},
    {"doctype": "Bizaxl Customer", "name": "CUST-003", "customer_name": "Amit Patel", "customer_type": "Individual", "mobile_no": "9876543212", "email": "amit@example.com", "pan": "CCAPL1234C", "date_of_birth": "1988-03-10", "occupation": "Business", "annual_income": 1500000},
    {"doctype": "Bizaxl Customer", "name": "CUST-004", "customer_name": "Sunita Devi", "customer_type": "Individual", "mobile_no": "9876543213", "email": "sunita@example.com", "pan": "DDAPL1234C", "date_of_birth": "1992-11-25", "occupation": "Salaried", "annual_income": 600000},
    {"doctype": "Bizaxl Customer", "name": "CUST-005", "customer_name": "Vikram Singh", "customer_type": "Individual", "mobile_no": "9876543214", "email": "vikram@example.com", "pan": "EEAPL1234C", "date_of_birth": "1987-07-08", "occupation": "Business", "annual_income": 2000000},
]
for c in customers:
    if create_doc(c["doctype"], c): count += 1

# KYC Documents
print("2. Creating KYC Documents...")
kyc_docs = [
    {"doctype": "KYC Document", "name": "KYC-001", "customer": "CUST-001", "document_type": "Aadhaar Card", "document_number": "1234-5678-9012", "upload_date": frappe.utils.today()},
    {"doctype": "KYC Document", "name": "KYC-002", "customer": "CUST-001", "document_type": "PAN Card", "document_number": "AAAPL1234C", "upload_date": frappe.utils.today()},
    {"doctype": "KYC Document", "name": "KYC-003", "customer": "CUST-002", "document_type": "Aadhaar Card", "document_number": "2345-6789-0123", "upload_date": frappe.utils.today()},
    {"doctype": "KYC Document", "name": "KYC-004", "customer": "CUST-003", "document_type": "Passport", "document_number": "J1234567", "upload_date": frappe.utils.today()},
]
for k in kyc_docs:
    if create_doc(k["doctype"], k): count += 1

# ============================================
# 2. BANKING & ACCOUNTS
# ============================================
print("3. Creating Bank Accounts...")
bank_accounts = [
    {"doctype": "Bank Account", "name": "BANK-001", "account_name": "Main Operations", "bank_name": "HDFC Bank", "account_number": "50100234567890", "ifsc_code": "HDFC0001234", "account_type": "Current", "branch": "Mumbai Main"},
    {"doctype": "Bank Account", "name": "BANK-002", "account_name": "Loan Disbursement", "bank_name": "ICICI Bank", "account_number": "50100234567891", "ifsc_code": "ICIC0001234", "account_type": "Current", "branch": "Delhi Main"},
    {"doctype": "Bank Account", "name": "BANK-003", "account_name": "Collections", "bank_name": "SBI", "account_number": "50100234567892", "ifsc_code": "SBIN0001234", "account_type": "Savings", "branch": "Chennai Main"},
]
for b in bank_accounts:
    if create_doc(b["doctype"], b): count += 1

print("4. Creating Transactions...")
today = frappe.utils.today()
for i in range(1, 11):
    tx_date = frappe.utils.add_days(today, -random.randint(1, 30))
    t = {
        "doctype": "Transaction",
        "name": f"TXN-{i:03d}",
        "transaction_type": random.choice(["Credit", "Debit"]),
        "amount": random.randint(1000, 50000),
        "transaction_date": tx_date,
        "reference_number": f"REF{tx_date.replace('-', '')}{i}",
        "description": random.choice(["Loan Disbursement", "EMI Payment", "Fee Collection", "Interest Credit"]),
    }
    if create_doc(t["doctype"], t): count += 1

# ============================================
# 3. INVESTMENTS
# ============================================
print("5. Creating Investment Accounts...")
investments = [
    {"doctype": "Investment Account", "name": "INV-001", "customer": "CUST-001", "investment_type": "Mutual Fund", "current_value": 250000, "purchase_value": 200000, "purchase_date": "2023-01-15"},
    {"doctype": "Investment Account", "name": "INV-002", "customer": "CUST-002", "investment_type": "Fixed Deposit", "current_value": 100000, "purchase_value": 100000, "purchase_date": "2023-06-01"},
    {"doctype": "Investment Account", "name": "INV-003", "customer": "CUST-003", "investment_type": "Digital Gold", "current_value": 50000, "purchase_value": 45000, "purchase_date": "2023-03-20"},
]
for inv in investments:
    if create_doc(inv["doctype"], inv): count += 1

print("6. Creating Mutual Funds...")
mutual_funds = [
    {"doctype": "Mutual Fund", "name": "MF-001", "fund_name": "HDFC Top 100", "fund_category": "Equity", "nav": 850.50, "last_updated": frappe.utils.today()},
    {"doctype": "Mutual Fund", "name": "MF-002", "fund_name": "ICICI Pru Balanced", "fund_category": "Hybrid", "nav": 250.75, "last_updated": frappe.utils.today()},
    {"doctype": "Mutual Fund", "name": "MF-003", "fund_name": "SBI Blue Chip", "fund_category": "Equity", "nav": 420.30, "last_updated": frappe.utils.today()},
]
for mf in mutual_funds:
    if create_doc(mf["doctype"], mf): count += 1

print("7. Creating Fixed Deposits...")
fixed_deposits = [
    {"doctype": "Fixed Deposit", "name": "FD-001", "customer": "CUST-001", "principal_amount": 500000, "interest_rate": 7.5, "tenure_months": 24, "maturity_date": "2025-01-15", "fd_type": "Cumulative"},
    {"doctype": "Fixed Deposit", "name": "FD-002", "customer": "CUST-002", "principal_amount": 200000, "interest_rate": 6.5, "tenure_months": 12, "maturity_date": "2024-06-01", "fd_type": "Monthly Payout"},
]
for fd in fixed_deposits:
    if create_doc(fd["doctype"], fd): count += 1

# ============================================
# 4. LOANS
# ============================================
print("8. Creating Loan Products...")
loan_products = [
    {"doctype": "Loan Product", "name": "LP-001", "product_name": "Personal Loan", "loan_type": "Personal", "min_amount": 50000, "max_amount": 5000000, "interest_rate": 14, "tenure_months_max": 60},
    {"doctype": "Loan Product", "name": "LP-002", "product_name": "Business Loan", "loan_type": "Business", "min_amount": 100000, "max_amount": 10000000, "interest_rate": 16, "tenure_months_max": 84},
    {"doctype": "Loan Product", "name": "LP-003", "product_name": "Home Loan", "loan_type": "Mortgage", "min_amount": 500000, "max_amount": 50000000, "interest_rate": 8.5, "tenure_months_max": 360},
    {"doctype": "Loan Product", "name": "LP-004", "product_name": "Gold Loan", "loan_type": "Secured", "min_amount": 10000, "max_amount": 5000000, "interest_rate": 10, "tenure_months_max": 24},
    {"doctype": "Loan Product", "name": "LP-005", "product_name": "Vehicle Loan", "loan_type": "Secured", "min_amount": 50000, "max_amount": 5000000, "interest_rate": 11, "tenure_months_max": 84},
]
for lp in loan_products:
    if create_doc(lp["doctype"], lp): count += 1

print("9. Creating Loan Applications...")
loan_apps = [
    {"doctype": "Loan Application", "name": "LA-001", "customer": "CUST-001", "loan_product": "LP-001", "loan_amount": 500000, "tenure_months": 36, "application_date": frappe.utils.today(), "status": "Approved"},
    {"doctype": "Loan Application", "name": "LA-002", "customer": "CUST-002", "loan_product": "LP-002", "loan_amount": 1000000, "tenure_months": 48, "application_date": frappe.utils.today(), "status": "Pending"},
    {"doctype": "Loan Application", "name": "LA-003", "customer": "CUST-003", "loan_product": "LP-003", "loan_amount": 5000000, "tenure_months": 240, "application_date": frappe.utils.today(), "status": "Processing"},
]
for la in loan_apps:
    if create_doc(la["doctype"], la): count += 1

print("10. Creating Loan Disbursements...")
disbursements = [
    {"doctype": "Loan Disbursement", "name": "DISB-001", "loan_application": "LA-001", "customer": "CUST-001", "disbursement_amount": 500000, "disbursement_date": frappe.utils.add_days(frappe.utils.today(), -15), "disbursement_mode": "Bank Transfer", "reference_number": "DISB/2024/001"},
]
for d in disbursements:
    if create_doc(d["doctype"], d): count += 1

print("11. Creating Loan Repayments...")
repayments = [
    {"doctype": "Loan Repayment", "name": "REP-001", "customer": "CUST-001", "loan_application": "LA-001", "repayment_amount": 17500, "repayment_date": frappe.utils.today(), "repayment_mode": "NACH", "principal_amount": 12000, "interest_amount": 5500},
]
for r in repayments:
    if create_doc(r["doctype"], r): count += 1

# ============================================
# 5. INSURANCE
# ============================================
print("12. Creating Insurance Products...")
ins_products = [
    {"doctype": "Insurance Product", "name": "INS-P-001", "product_name": "Term Life Insurance", "insurance_type": "Life", "sum_assured_min": 100000, "sum_assured_max": 50000000, "premium_min": 500, "premium_max": 500000},
    {"doctype": "Insurance Product", "name": "INS-P-002", "product_name": "Health Insurance", "insurance_type": "Health", "sum_assured_min": 100000, "sum_assured_max": 10000000, "premium_min": 300, "premium_max": 100000},
]
for ip in ins_products:
    if create_doc(ip["doctype"], ip): count += 1

print("13. Creating Insurance Policies...")
ins_policies = [
    {"doctype": "Insurance Policy", "name": "POL-001", "customer": "CUST-001", "insurance_product": "INS-P-001", "policy_number": "POL/LIFE/2024/001", "sum_assured": 5000000, "premium_amount": 25000, "premium_frequency": "Annual", "policy_start_date": "2024-01-01", "policy_end_date": "2034-01-01", "status": "Active"},
    {"doctype": "Insurance Policy", "name": "POL-002", "customer": "CUST-002", "insurance_product": "INS-P-002", "policy_number": "POL/HEALTH/2024/002", "sum_assured": 1000000, "premium_amount": 12000, "premium_frequency": "Annual", "policy_start_date": "2024-03-01", "policy_end_date": "2025-03-01", "status": "Active"},
]
for pol in ins_policies:
    if create_doc(pol["doctype"], pol): count += 1

# ============================================
# 6. CREDIT MANAGEMENT
# ============================================
print("14. Creating Credit Reports...")
credit_reports = [
    {"doctype": "Credit Report", "name": "CR-001", "customer": "CUST-001", "bureau": "CIBIL", "score": 785, "report_date": frappe.utils.today()},
    {"doctype": "Credit Report", "name": "CR-002", "customer": "CUST-002", "bureau": "CIBIL", "score": 720, "report_date": frappe.utils.today()},
    {"doctype": "Credit Report", "name": "CR-003", "customer": "CUST-003", "bureau": "Experian", "score": 810, "report_date": frappe.utils.today()},
]
for cr in credit_reports:
    if create_doc(cr["doctype"], cr): count += 1

# ============================================
# 7. PORTFOLIO MANAGEMENT
# ============================================
print("15. Creating Portfolio Holdings...")
portfolio = [
    {"doctype": "Portfolio Holding", "name": "PH-001", "customer": "CUST-001", "asset_type": "Mutual Funds", "current_value": 250000, "cost_value": 200000, "allocation_percentage": 40},
    {"doctype": "Portfolio Holding", "name": "PH-002", "customer": "CUST-001", "asset_type": "Fixed Deposits", "current_value": 200000, "cost_value": 200000, "allocation_percentage": 32},
    {"doctype": "Portfolio Holding", "name": "PH-003", "customer": "CUST-001", "asset_type": "Gold", "current_value": 100000, "cost_value": 85000, "allocation_percentage": 16},
    {"doctype": "Portfolio Holding", "name": "PH-004", "customer": "CUST-001", "asset_type": "Stocks", "current_value": 75000, "cost_value": 60000, "allocation_percentage": 12},
]
for p in portfolio:
    if create_doc(p["doctype"], p): count += 1

# ============================================
# 8. PAYMENTS & BILLS
# ============================================
print("16. Creating Bill Payments...")
bill_payments = [
    {"doctype": "Bill Payment", "name": "BP-001", "customer": "CUST-001", "bill_type": "Electricity", "bill_number": "EB/2024/001", "amount": 2500, "payment_date": frappe.utils.today(), "status": "Success"},
    {"doctype": "Bill Payment", "name": "BP-002", "customer": "CUST-002", "bill_type": "Mobile", "bill_number": "MOB/2024/001", "amount": 500, "payment_date": frappe.utils.today(), "status": "Success"},
    {"doctype": "Bill Payment", "name": "BP-003", "customer": "CUST-003", "bill_type": "DTH", "bill_number": "DTH/2024/001", "amount": 800, "payment_date": frappe.utils.today(), "status": "Success"},
]
for bp in bill_payments:
    if create_doc(bp["doctype"], bp): count += 1

print("17. Creating Mobile Recharges...")
recharges = [
    {"doctype": "Mobile Recharge", "name": "RECH-001", "customer": "CUST-001", "mobile_number": "9876543210", "operator": "Airtel", "plan_type": "Prepaid", "amount": 299, "recharge_date": frappe.utils.today()},
    {"doctype": "Mobile Recharge", "name": "RECH-002", "customer": "CUST-002", "mobile_number": "9876543211", "operator": "Jio", "plan_type": "Prepaid", "amount": 499, "recharge_date": frappe.utils.today()},
]
for rc in recharges:
    if create_doc(rc["doctype"], rc): count += 1

# ============================================
# 9. COLLECTIONS
# ============================================
print("18. Creating Collection Records...")
collections = [
    {"doctype": "Collection Record", "name": "COL-001", "customer": "CUST-001", "collection_type": "EMI", "amount_due": 17500, "amount_collected": 17500, "collection_date": frappe.utils.today(), "status": "Collected"},
    {"doctype": "Collection Record", "name": "COL-002", "customer": "CUST-002", "collection_type": "EMI", "amount_due": 25000, "amount_collected": 25000, "collection_date": frappe.utils.today(), "status": "Collected"},
    {"doctype": "Collection Record", "name": "COL-003", "customer": "CUST-003", "collection_type": "EMI", "amount_due": 45000, "amount_collected": 30000, "collection_date": frappe.utils.today(), "status": "Partial"},
]
for col in collections:
    if create_doc(col["doctype"], col): count += 1

# ============================================
# 10. RISK & COMPLIANCE
# ============================================
print("19. Creating AML Screenings...")
aml = [
    {"doctype": "AML Screening", "name": "AML-001", "customer": "CUST-001", "screening_type": "Initial", "result": "Clear", "screening_date": frappe.utils.today()},
    {"doctype": "AML Screening", "name": "AML-002", "customer": "CUST-002", "screening_type": "Periodic", "result": "Clear", "screening_date": frappe.utils.today()},
]
for a in aml:
    if create_doc(a["doctype"], a): count += 1

print("20. Creating Fraud Alerts...")
fraud_alerts = [
    {"doctype": "Fraud Alert", "name": "FRAUD-001", "customer": "CUST-001", "alert_type": "Suspicious Activity", "description": "Multiple failed login attempts", "status": "Resolved", "alert_date": frappe.utils.today()},
]
for f in fraud_alerts:
    if create_doc(f["doctype"], f): count += 1

# ============================================
# 11. ACCOUNTING
# ============================================
print("21. Creating GL Settings...")
if not frappe.db.exists("GL Settings", "GL Settings"):
    try:
        gl = frappe.get_doc({
            "doctype": "GL Settings",
            "name": "GL Settings",
            "company": "Bizaxl Finance",
            "default_currency": "INR",
        })
        gl.insert(ignore_permissions=True)
        frappe.db.commit()
        count += 1
    except:
        pass

# ============================================
# 12. DSA & LEADS
# ============================================
print("22. Creating DSA Masters...")
dsa = [
    {"doctype": "DSA Master", "name": "DSA-001", "dsa_name": "ABC Financial Services", "contact_person": "John Doe", "mobile": "9876543200", "email": "john@abc.com", "region": "North", "status": "Active"},
    {"doctype": "DSA Master", "name": "DSA-002", "dsa_name": "XYZ Consultants", "contact_person": "Jane Smith", "mobile": "9876543201", "email": "jane@xyz.com", "region": "South", "status": "Active"},
]
for d in dsa:
    if create_doc(d["doctype"], d): count += 1

print("23. Creating Leads...")
leads = [
    {"doctype": "Lead", "name": "LEAD-001", "lead_name": "Ramesh Kumar", "email_id": "ramesh@example.com", "mobile_no": "9876543299", "lead_source": "DSA", "status": "Open", "customer_type": "Individual"},
    {"doctype": "Lead", "name": "LEAD-002", "lead_name": "Suresh Patel", "email_id": "suresh@example.com", "mobile_no": "9876543298", "lead_source": "Website", "status": "Open", "customer_type": "Business"},
    {"doctype": "Lead", "name": "LEAD-003", "lead_name": "Ganesh Iyer", "email_id": "ganesh@example.com", "mobile_no": "9876543297", "lead_source": "Reference", "status": "Converted", "customer_type": "Individual"},
]
for l in leads:
    if create_doc(l["doctype"], l): count += 1

# ============================================
# 24. CHIT FUND
# ============================================
print("24. Creating Chit Groups...")
chit_groups = [
    {"doctype": "Chit Group", "name": "CHIT-001", "group_name": "Mysore Gold Chit 30", "chit_value": 300000, "total_months": 30, "monthly_subscription": 10000, "start_date": "2024-01-01", "status": "Active"},
]
for cg in chit_groups:
    if create_doc(cg["doctype"], cg): count += 1

print("25. Creating Chit Subscribers...")
chit_subs = [
    {"doctype": "Chit Subscriber", "name": "CHS-001", "chit_group": "CHIT-001", "customer": "CUST-001", "subscriber_number": 1, "join_date": "2024-01-01", "status": "Active"},
    {"doctype": "Chit Subscriber", "name": "CHS-002", "chit_group": "CHIT-001", "customer": "CUST-002", "subscriber_number": 2, "join_date": "2024-01-01", "status": "Active"},
]
for cs in chit_subs:
    if create_doc(cs["doctype"], cs): count += 1

# ============================================
# 26. RETAILER & POS
# ============================================
print("26. Creating Retailer Masters...")
retailers = [
    {"doctype": "Retailer Master", "name": "RET-001", "retailer_name": "ABC Electronics", "owner_name": "Ravi Kumar", "mobile": "9876543300", "city": "Bangalore", "category": "Electronics", "status": "Active"},
    {"doctype": "Retailer Master", "name": "RET-002", "retailer_name": "XYZ Furniture", "owner_name": "Suresh", "mobile": "9876543301", "city": "Mumbai", "category": "Furniture", "status": "Active"},
]
for rt in retailers:
    if create_doc(rt["doctype"], rt): count += 1

print("27. Creating POS Transactions...")
pos_txns = [
    {"doctype": "POS Transaction", "name": "POS-001", "retailer": "RET-001", "customer": "CUST-001", "invoice_number": "INV/POS/001", "amount": 25000, "transaction_date": frappe.utils.today(), "payment_mode": "EMI"},
    {"doctype": "POS Transaction", "name": "POS-002", "retailer": "RET-002", "customer": "CUST-002", "invoice_number": "INV/POS/002", "amount": 45000, "transaction_date": frappe.utils.today(), "payment_mode": "BNPL"},
]
for pt in pos_txns:
    if create_doc(pt["doctype"], pt): count += 1

# ============================================
# 27. BNPL
# ============================================
print("28. Creating BNPL Orders...")
bnpl_orders = [
    {"doctype": "BNPL Order", "name": "BNPL-001", "customer": "CUST-001", "merchant": "Amazon", "order_amount": 15000, "down_payment": 5000, "tenure_months": 3, "order_date": frappe.utils.today(), "status": "Active"},
    {"doctype": "BNPL Order", "name": "BNPL-002", "customer": "CUST-002", "merchant": "Flipkart", "order_amount": 25000, "down_payment": 5000, "tenure_months": 6, "order_date": frappe.utils.today(), "status": "Active"},
]
for bo in bnpl_orders:
    if create_doc(bo["doctype"], bo): count += 1

# ============================================
print("\n" + "=" * 60)
print(f"✅ DEMO DATA LOADED SUCCESSFULLY!")
print(f"   Total records created: {count}")
print("=" * 60)
