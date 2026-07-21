"""
Demo Data API - Access via browser:
https://finance.bizaxl.local/api/method/bizaxl_finance.www.demo_data.load_demo_data
"""

import frappe
import random
from frappe import _

no_cache = 1
no_sitemap = 1

@frape.whitelist()
def load_demo_data():
    """API to load demo data - call this from browser"""
    
    result = {"success": False, "message": "", "count": 0}
    created = []
    
    try:
        # Helper function
        def create_doc(doctype, data):
            try:
                name = data.get("name")
                if not name:
                    return False
                if not frappe.db.exists(doctype, name):
                    doc = frappe.get_doc({
                        "doctype": doctype,
                        **{k: v for k, v in data.items() if k != "doctype"}
                    })
                    doc.insert(ignore_permissions=True)
                    return True
            except Exception as e:
                pass
            return False
        
        count = 0
        
        # 1. Customers
        customers = [
            {"name": "CUST-001", "customer_name": "Rajesh Kumar", "customer_type": "Individual", "mobile_no": "9876543210", "email": "rajesh@example.com", "annual_income": 1200000},
            {"name": "CUST-002", "customer_name": "Priya Sharma", "customer_type": "Individual", "mobile_no": "9876543211", "email": "priya@example.com", "annual_income": 800000},
            {"name": "CUST-003", "customer_name": "Amit Patel", "customer_type": "Individual", "mobile_no": "9876543212", "email": "amit@example.com", "annual_income": 1500000},
            {"name": "CUST-004", "customer_name": "Sunita Devi", "customer_type": "Individual", "mobile_no": "9876543213", "email": "sunita@example.com", "annual_income": 600000},
            {"name": "CUST-005", "customer_name": "Vikram Singh", "customer_type": "Individual", "mobile_no": "9876543214", "email": "vikram@example.com", "annual_income": 2000000},
        ]
        for c in customers:
            if create_doc("Bizaxl Customer", c):
                count += 1
                created.append(c["name"])
        
        # 2. Loan Products
        loan_products = [
            {"name": "LP-001", "product_name": "Personal Loan", "loan_type": "Personal", "min_amount": 50000, "max_amount": 5000000, "interest_rate": 14, "tenure_months_max": 60},
            {"name": "LP-002", "product_name": "Business Loan", "loan_type": "Business", "min_amount": 100000, "max_amount": 10000000, "interest_rate": 16, "tenure_months_max": 84},
            {"name": "LP-003", "product_name": "Home Loan", "loan_type": "Mortgage", "min_amount": 500000, "max_amount": 50000000, "interest_rate": 8.5, "tenure_months_max": 360},
            {"name": "LP-004", "product_name": "Gold Loan", "loan_type": "Secured", "min_amount": 10000, "max_amount": 5000000, "interest_rate": 10, "tenure_months_max": 24},
            {"name": "LP-005", "product_name": "Vehicle Loan", "loan_type": "Secured", "min_amount": 50000, "max_amount": 5000000, "interest_rate": 11, "tenure_months_max": 84},
        ]
        for lp in loan_products:
            if create_doc("Loan Product", lp):
                count += 1
                created.append(lp["name"])
        
        # 3. Loan Applications
        for i in range(1, 6):
            la = {
                "name": f"LA-{i:03d}",
                "customer": f"CUST-00{random.randint(1,5)}",
                "loan_product": f"LP-00{random.randint(1,5)}",
                "loan_amount": random.randint(100000, 2000000),
                "tenure_months": random.choice([12, 24, 36, 48, 60]),
                "application_date": frappe.utils.today(),
                "status": random.choice(["Approved", "Pending", "Processing"])
            }
            if create_doc("Loan Application", la):
                count += 1
                created.append(la["name"])
        
        # 4. Transactions
        for i in range(1, 21):
            tx = {
                "name": f"TXN-{i:03d}",
                "transaction_type": random.choice(["Credit", "Debit"]),
                "amount": random.randint(1000, 100000),
                "transaction_date": frappe.utils.add_days(frappe.utils.today(), -random.randint(1, 30)),
                "reference_number": f"REF{random.randint(100000, 999999)}"
            }
            if create_doc("Transaction", tx):
                count += 1
                created.append(tx["name"])
        
        # 5. Bank Accounts
        banks = [
            {"name": "BANK-001", "account_name": "Main Operations", "bank_name": "HDFC Bank", "account_number": "50100234567890", "ifsc_code": "HDFC0001234"},
            {"name": "BANK-002", "account_name": "Loan Disbursement", "bank_name": "ICICI Bank", "account_number": "50100234567891", "ifsc_code": "ICIC0001234"},
            {"name": "BANK-003", "account_name": "Collections", "bank_name": "SBI", "account_number": "50100234567892", "ifsc_code": "SBIN0001234"},
        ]
        for b in banks:
            if create_doc("Bank Account", b):
                count += 1
                created.append(b["name"])
        
        # 6. Leads
        for i in range(1, 6):
            lead = {
                "name": f"LEAD-{i:03d}",
                "lead_name": f"Lead Customer {i}",
                "email_id": f"lead{i}@example.com",
                "mobile_no": f"9876543{i:03d}",
                "lead_source": random.choice(["Website", "DSA", "Reference"]),
                "status": "Open"
            }
            if create_doc("Lead", lead):
                count += 1
                created.append(lead["name"])
        
        # 7. Investment Accounts
        for i in range(1, 5):
            inv = {
                "name": f"INV-{i:03d}",
                "customer": f"CUST-00{i}",
                "investment_type": random.choice(["Mutual Funds", "Fixed Deposit", "Digital Gold"]),
                "current_value": random.randint(50000, 500000),
                "purchase_value": random.randint(40000, 450000)
            }
            if create_doc("Investment Account", inv):
                count += 1
                created.append(inv["name"])
        
        # 8. Insurance Policies
        for i in range(1, 6):
            pol = {
                "name": f"POL-{i:03d}",
                "customer": f"CUST-00{random.randint(1,5)}",
                "policy_number": f"POL/2024/{i:03d}",
                "sum_assured": random.randint(100000, 5000000),
                "premium_amount": random.randint(5000, 50000),
                "status": "Active"
            }
            if create_doc("Insurance Policy", pol):
                count += 1
                created.append(pol["name"])
        
        # 9. Credit Reports
        for i in range(1, 8):
            cr = {
                "name": f"CR-{i:03d}",
                "customer": f"CUST-00{random.randint(1,5)}",
                "bureau": random.choice(["CIBIL", "Experian", "Equifax"]),
                "score": random.randint(650, 850),
                "report_date": frappe.utils.today()
            }
            if create_doc("Credit Report", cr):
                count += 1
                created.append(cr["name"])
        
        # 10. Bill Payments
        for i in range(1, 10):
            bp = {
                "name": f"BP-{i:03d}",
                "customer": f"CUST-00{random.randint(1,5)}",
                "bill_type": random.choice(["Electricity", "Water", "Gas", "Mobile"]),
                "amount": random.randint(200, 5000),
                "payment_date": frappe.utils.today(),
                "status": "Success"
            }
            if create_doc("Bill Payment", bp):
                count += 1
                created.append(bp["name"])
        
        # 11. Collection Records
        for i in range(1, 6):
            col = {
                "name": f"COL-{i:03d}",
                "customer": f"CUST-00{random.randint(1,5)}",
                "collection_type": "EMI",
                "amount_due": random.randint(10000, 50000),
                "amount_collected": random.randint(10000, 50000),
                "collection_date": frappe.utils.today(),
                "status": "Collected"
            }
            if create_doc("Collection Record", col):
                count += 1
                created.append(col["name"])
        
        # 12. AML Screenings
        for i in range(1, 5):
            aml = {
                "name": f"AML-{i:03d}",
                "customer": f"CUST-00{random.randint(1,5)}",
                "screening_type": "Initial",
                "result": "Clear",
                "screening_date": frappe.utils.today()
            }
            if create_doc("AML Screening", aml):
                count += 1
                created.append(aml["name"])
        
        # 13. DSA Masters
        for i in range(1, 4):
            dsa = {
                "name": f"DSA-{i:03d}",
                "dsa_name": f"DSA Partner {i}",
                "contact_person": f"Contact {i}",
                "mobile": f"9876543{i:03d}",
                "region": random.choice(["North", "South", "East", "West"]),
                "status": "Active"
            }
            if create_doc("DSA Master", dsa):
                count += 1
                created.append(dsa["name"])
        
        frappe.db.commit()
        
        result["success"] = True
        result["message"] = f"Successfully loaded {count} demo records!"
        result["count"] = count
        
    except Exception as e:
        result["message"] = str(e)
    
    return result


def get_context(context):
    context.title = "Load Demo Data"
