"""
Bizaxl Finance Platform — Demo Data Loader
============================================
Populates all 106+ DocTypes with realistic demo data.

Usage on server:
    bench --site your-site console
    exec(open("../apps/bizaxl_finance/bizaxl_finance/load_demo_data.py").read())

Or via bench:
    bench --site your-site execute bizaxl_finance.load_demo_data.load_demo_data

NOTE: Everything is inside load_demo_data() as inner functions.
This is REQUIRED because Frappe console's exec() does not properly
propagate module-level imports to function __globals__.
"""

import frappe
import random
import math


def load_demo_data():
    # ── Imports inside the function for closures ──
    # exec() in Frappe console doesn't propagate module-level imports
    # to inner function closures. These must be in the enclosing scope.
    import random
    import math
    from frappe.utils import today, add_months, add_days, add_years

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _safe_insert(data, ignore_duplicate=True):
        try:
            doc = frappe.get_doc(data)
            doc.insert(ignore_permissions=True, ignore_if_duplicate=ignore_duplicate)
            return doc.name
        except frappe.DuplicateEntryError:
            return frappe.db.get_value(
                data["doctype"], data.get("name") or data.get(
                    data["doctype"].lower().replace(" ", "_")
                )
            )
        except Exception as e:
            print(f"    ⚠️ FAILED {data['doctype']}: {e}")
            return None

    def _rand_amount(min_v, max_v):
        return round(random.uniform(min_v, max_v), 2)

    def _rand_int(min_v, max_v):
        return random.randint(min_v, max_v)

    # ═════════════════════════════════════════════════════════════════════════
    # 1. FOUNDATION
    # ═════════════════════════════════════════════════════════════════════════
    def _load_foundation():
        print("\n📦 FOUNDATION MODULE")
        for c in [
            {"company_name": "Bizaxl Finance Ltd", "company_type": "NBFC", "nbfc_category": "NBFC-ND-SI",
             "city": "Mumbai", "state": "Maharashtra", "pincode": "400001",
             "gstin": "27AAECB1234D1Z5", "pan": "AAECB1234D", "is_fiu_registered": 1, "is_ciibil_member": 1,
             "quarter_end_month": "March"},
            {"company_name": "Bizaxl Microfinance Pvt Ltd", "company_type": "NBFC-MFI",
             "city": "Chennai", "state": "Tamil Nadu", "pincode": "600001",
             "gstin": "33AAECM5678E1Z5", "pan": "AAECM5678E", "is_fiu_registered": 1, "is_ciibil_member": 1,
             "quarter_end_month": "June"},
        ]:
            _safe_insert({"doctype": "Company Config", **c})
        print("  ✅ Company Configs created")

        for b in [
            {"branch_name": "Head Office - Mumbai", "city": "Mumbai", "state": "Maharashtra", "is_head_office": 1},
            {"branch_name": "Chennai Branch", "city": "Chennai", "state": "Tamil Nadu"},
            {"branch_name": "Delhi Branch", "city": "New Delhi", "state": "Delhi"},
            {"branch_name": "Bangalore Branch", "city": "Bangalore", "state": "Karnataka"},
            {"branch_name": "Hyderabad Branch", "city": "Hyderabad", "state": "Telangana"},
            {"branch_name": "Kolkata Branch", "city": "Kolkata", "state": "West Bengal"},
        ]:
            _safe_insert({"doctype": "Branch Master", **b})
        print("  ✅ Branch Masters created")

        for r in [
            {"rate_name": "Personal Loan - Base", "loan_type": "Personal Loan", "base_rate": 10.99,
             "minimum_rate": 9.99, "maximum_rate": 24.00, "rate_type": "Fixed"},
            {"rate_name": "Home Loan - MCLR Linked", "loan_type": "Home Loan", "base_rate": 8.50,
             "minimum_rate": 7.50, "maximum_rate": 14.00, "rate_type": "Floating"},
            {"rate_name": "Gold Loan - Base", "loan_type": "Gold Loan", "base_rate": 7.50,
             "minimum_rate": 6.00, "maximum_rate": 18.00, "rate_type": "Reducing"},
            {"rate_name": "Business Loan - Base", "loan_type": "Business Loan", "base_rate": 12.50,
             "minimum_rate": 10.00, "maximum_rate": 22.00, "rate_type": "Floating"},
        ]:
            _safe_insert({"doctype": "Interest Rate Engine", "naming_series": "IR-.YYYY.-.####", **r})
        print("  ✅ Interest Rate Engines created")

        for c in [
            {"charge_name": "Processing Fee - Personal Loan", "charge_type": "Processing Fee", "percentage": 2.0,
             "applicable_on": "Personal Loan"},
            {"charge_name": "Prepayment Charges - Home Loan", "charge_type": "Prepayment Penalty", "percentage": 2.5,
             "applicable_on": "Home Loan"},
            {"charge_name": "Late Payment Penalty", "charge_type": "Late Payment", "percentage": 2.0,
             "applicable_on": "All Loans"},
            {"charge_name": "Statement Reprint Fee", "charge_type": "Service Fee", "amount": 100,
             "applicable_on": "All Loans"},
        ]:
            _safe_insert({"doctype": "Charge Rule", **c})
        print("  ✅ Charge Rules created")

    # ═════════════════════════════════════════════════════════════════════════
    # 2. CUSTOMER MANAGEMENT
    # ═════════════════════════════════════════════════════════════════════════
    def _load_customers():
        print("\n👤 CUSTOMER MANAGEMENT MODULE")

        leads_data = [
            {"lead_name": "Rajesh Kumar", "company_name": "RK Enterprises", "mobile": "9876543210",
             "email": "rajesh@rkenterprises.com", "lead_status": "Converted", "source": "Website", "city": "Mumbai"},
            {"lead_name": "Priya Sharma", "company_name": "Priya's Boutique", "mobile": "9876543211",
             "email": "priya@boutique.com", "lead_status": "Converted", "source": "Reference", "city": "Delhi"},
            {"lead_name": "Amit Patel", "company_name": "Patel Constructions", "mobile": "9876543212",
             "email": "amit@patelcon.com", "lead_status": "Contacted", "source": "DSA", "city": "Bangalore"},
            {"lead_name": "Sunita Reddy", "company_name": "Reddy Associates", "mobile": "9876543213",
             "email": "sunita@reddyassoc.com", "lead_status": "New", "source": "Website", "city": "Hyderabad"},
            {"lead_name": "Vikram Singh", "mobile": "9876543214", "email": "vikram.singh@gmail.com",
             "lead_status": "Qualified", "source": "Facebook", "city": "Chennai"},
        ]
        for l in leads_data:
            _safe_insert({
                "doctype": "Lead", "naming_series": "LEAD-.YYYY.-.####",
                "lead_name": l["lead_name"], "company_name": l.get("company_name"),
                "mobile_number": l["mobile"], "email": l["email"],
                "status": l["lead_status"], "source": l["source"], "city": l["city"],
            })
        print("  ✅ Leads created")

        for d in [
            {"dsa_name": "FinPartners India", "contact_person": "Suresh Iyer", "contact_number": "9988776655",
             "commission_rate": 1.5, "city": "Mumbai", "status": "Active"},
            {"dsa_name": "LoanBazaar Associates", "contact_person": "Meena Joshi", "contact_number": "9988776656",
             "commission_rate": 2.0, "city": "Delhi", "status": "Active"},
        ]:
            _safe_insert({"doctype": "DSA Master", "naming_series": "DSA-.YYYY.-.####", **d})
        print("  ✅ DSA Masters created")

        customers_data = [
            {"customer_name": "Rajesh Kumar", "customer_type": "Sole Proprietor", "mobile": "9876543210",
             "email": "rajesh@rkenterprises.com", "pan_number": "ABCDE1234F", "aadhaar_number": "123456789012",
             "ckyc_number": "CKYC100001", "kyc_status": "Verified", "risk_profile": "Medium",
             "annual_income": 1200000, "city": "Mumbai", "state": "Maharashtra", "employment_type": "Self-Employed"},
            {"customer_name": "Priya Sharma", "customer_type": "Individual", "mobile": "9876543211",
             "email": "priya@boutique.com", "pan_number": "FGHIJ5678K", "aadhaar_number": "234567890123",
             "ckyc_number": "CKYC100002", "kyc_status": "Verified", "risk_profile": "Low",
             "annual_income": 850000, "city": "Delhi", "state": "Delhi", "employment_type": "Business Owner"},
            {"customer_name": "Vikram Singh", "customer_type": "Individual", "mobile": "9876543214",
             "email": "vikram.singh@gmail.com", "pan_number": "KLMNO9012P", "aadhaar_number": "345678901234",
             "ckyc_number": "CKYC100003", "kyc_status": "Under Review", "risk_profile": "Low",
             "annual_income": 600000, "city": "Chennai", "state": "Tamil Nadu", "employment_type": "Salaried"},
            {"customer_name": "Ananya Desai", "mobile": "9876543215", "email": "ananya.d@gmail.com",
             "pan_number": "PQRST3456U", "aadhaar_number": "456789012345", "ckyc_number": "CKYC100004",
             "kyc_status": "Verified", "risk_profile": "Medium", "annual_income": 1800000,
             "city": "Bangalore", "state": "Karnataka", "employment_type": "Self-Employed"},
            {"customer_name": "Mohan Gupta", "mobile": "9876543216", "email": "mohan.gupta@gmail.com",
             "pan_number": "UVWXY7890Z", "aadhaar_number": "567890123456", "ckyc_number": "CKYC100005",
             "kyc_status": "Verified", "risk_profile": "High", "annual_income": 3600000,
             "city": "Mumbai", "state": "Maharashtra", "employment_type": "Business Owner"},
            {"customer_name": "Lakshmi Narayanan", "customer_type": "Individual", "mobile": "9876543217",
             "email": "lakshmi.n@gmail.com", "pan_number": "ZABCD1234E", "aadhaar_number": "678901234567",
             "ckyc_number": "CKYC100006", "kyc_status": "Verified", "risk_profile": "Medium",
             "annual_income": 2400000, "city": "Chennai", "state": "Tamil Nadu", "employment_type": "Salaried"},
        ]
        for c in customers_data:
            _safe_insert({
                "doctype": "Bizaxl Customer", "naming_series": "CUST-.YYYY.-.####",
                "customer_name": c["customer_name"], "customer_type": c.get("customer_type", "Individual"),
                "mobile_number": c["mobile"], "email": c["email"],
                "pan_number": c["pan_number"], "aadhaar_number": c["aadhaar_number"],
                "ckyc_number": c.get("ckyc_number"), "kyc_status": c["kyc_status"],
                "risk_profile": c["risk_profile"], "annual_income": c["annual_income"],
                "city": c["city"], "state": c["state"], "employment_type": c["employment_type"],
                "customer_status": "Active", "is_verified": 1 if c["kyc_status"] == "Verified" else 0,
            })
        print("  ✅ Bizaxl Customers created")

        for cust_name in ["Rajesh Kumar", "Priya Sharma", "Vikram Singh"]:
            cust = frappe.db.get_value("Bizaxl Customer", {"customer_name": cust_name})
            if cust:
                _safe_insert({
                    "doctype": "Customer Nomination", "customer": cust,
                    "nominee_name": f"Nominee of {cust_name}", "relationship": "Spouse",
                    "nominee_date_of_birth": "1985-06-15", "nominee_percentage": 100,
                })
        print("  ✅ Customer Nominations created")

        for cust_name in ["Rajesh Kumar", "Priya Sharma", "Ananya Desai"]:
            cust = frappe.db.get_value("Bizaxl Customer", {"customer_name": cust_name})
            if cust:
                _safe_insert({
                    "doctype": "KYC Document", "customer": cust,
                    "document_type": "Aadhaar Card", "document_number": f"KYC-{random.randint(1000,9999)}",
                    "document_status": "Verified", "verification_date": add_days(today(), -_rand_int(30, 180)),
                })
        print("  ✅ KYC Documents created")

    # ═════════════════════════════════════════════════════════════════════════
    # 3. BANKING
    # ═════════════════════════════════════════════════════════════════════════
    def _load_banking():
        print("\n🏦 BANKING MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"])
        banks = ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra"]
        account_types = ["Savings", "Current", "Salary"]

        for cust in customers[:4]:
            for _ in range(random.randint(1, 2)):
                _safe_insert({
                    "doctype": "Bank Account", "customer": cust.name,
                    "account_name": f"{cust.customer_name} - {random.choice(banks)}",
                    "bank_name": random.choice(banks), "account_type": random.choice(account_types),
                    "account_number": f"XXXX{random.randint(1000,9999)}",
                    "current_balance": _rand_amount(10000, 500000),
                    "ifsc_code": f"{random.choice(['HDFC','ICICI','SBIN','UTIB'])}000{random.randint(1000,9999)}",
                    "is_active": 1,
                })
        print("  ✅ Bank Accounts created")

        upi_handles = ["@paytm", "@googlepay", "@phonepe", "@axisbank", "@icici"]
        for cust in customers[:4]:
            _safe_insert({
                "doctype": "UPI ID", "customer": cust.name,
                "upi_id": f"{cust.customer_name.lower().replace(' ','')}{random.choice(upi_handles)}",
                "is_primary": 1, "status": "Active",
            })
        print("  ✅ UPI IDs created")

        txn_cats = ["Online Transfer", "NEFT", "UPI Payment", "Bill Payment", "ATM Withdrawal", "Salary Credit", "FD Maturity"]
        for cust in customers[:4]:
            for _ in range(random.randint(5, 10)):
                txn_type = random.choice(["Credit", "Debit"])
                _safe_insert({
                    "doctype": "Transaction", "customer": cust.name, "transaction_type": txn_type,
                    "transaction_category": random.choice(txn_cats), "amount": _rand_amount(500, 50000),
                    "transaction_date": add_days(today(), -_rand_int(1, 90)), "status": "Completed",
                    "description": f"{txn_type} via {random.choice(['UPI','NEFT','IMPS'])}",
                })
        print("  ✅ Transactions created")

    # ═════════════════════════════════════════════════════════════════════════
    # 4. LOANS
    # ═════════════════════════════════════════════════════════════════════════
    def _load_loans():
        print("\n💰 LOANS MODULE")
        products = [
            {"loan_product_name": "Personal Loan - Standard", "loan_type": "Personal Loan",
             "interest_rate": 10.99, "processing_fee": 2.0, "min_amount": 50000, "max_amount": 2500000,
             "min_tenure_months": 6, "max_tenure_months": 60},
            {"loan_product_name": "Home Loan - DreamHome", "loan_type": "Home Loan",
             "interest_rate": 8.50, "processing_fee": 1.5, "min_amount": 500000, "max_amount": 10000000,
             "min_tenure_months": 12, "max_tenure_months": 360},
            {"loan_product_name": "Gold Loan - Swarna", "loan_type": "Gold Loan",
             "interest_rate": 7.50, "processing_fee": 0.5, "min_amount": 10000, "max_amount": 1000000,
             "min_tenure_months": 3, "max_tenure_months": 24},
            {"loan_product_name": "Business Loan - Vyapar", "loan_type": "Business Loan",
             "interest_rate": 12.50, "processing_fee": 2.5, "min_amount": 200000, "max_amount": 5000000,
             "min_tenure_months": 12, "max_tenure_months": 84},
            {"loan_product_name": "Education Loan - Vidya", "loan_type": "Education Loan",
             "interest_rate": 9.50, "processing_fee": 1.0, "min_amount": 100000, "max_amount": 2000000,
             "min_tenure_months": 12, "max_tenure_months": 180},
            {"loan_product_name": "Vehicle Loan - DriveEasy", "loan_type": "Auto Loan",
             "interest_rate": 9.00, "processing_fee": 1.5, "min_amount": 100000, "max_amount": 3000000,
             "min_tenure_months": 12, "max_tenure_months": 84},
        ]
        for p in products:
            _safe_insert({"doctype": "Loan Product", **p})
        print("  ✅ Loan Products created")

        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name", "annual_income"])
        statuses = ["Disbursed", "Disbursed", "Approved", "Under Review", "Disbursed", "Disbursed"]

        for i, cust in enumerate(customers[:6]):
            product = random.choice(products)
            amount = _rand_amount(product["min_amount"], min(product["max_amount"], 1000000))
            tenure = _rand_int(max(6, product["min_tenure_months"]), min(60, product["max_tenure_months"]))
            rate = product["interest_rate"] + random.choice([0, 0.5, 1, -0.5])
            status = statuses[i]

            loan_app = _safe_insert({
                "doctype": "Loan Application", "naming_series": "LA-.YYYY.-.####",
                "customer": cust.name, "customer_name": cust.customer_name,
                "loan_product": product["loan_product_name"], "loan_amount": amount,
                "tenure_months": tenure, "interest_rate": rate, "status": status,
                "application_date": add_days(today(), -_rand_int(30, 180)),
                "purpose": random.choice(["Business Expansion", "Home Purchase", "Education", "Medical", "Wedding", "Debt Consolidation"]),
                "credit_score": _rand_int(650, 850),
            })
            if loan_app and status == "Disbursed":
                disb = _safe_insert({
                    "doctype": "Loan Disbursement", "naming_series": "LD-.YYYY.-.####",
                    "loan_application": loan_app, "customer": cust.name, "customer_name": cust.customer_name,
                    "disbursement_amount": amount, "disbursement_date": add_days(today(), -_rand_int(15, 90)),
                    "interest_rate": rate, "tenure_months": tenure, "status": "Disbursed",
                    "mode_of_payment": random.choice(["Bank Transfer", "NEFT", "RTGS"]),
                    "processing_fee_percentage": product["processing_fee"],
                })
                if disb:
                    emi = round(amount * (rate / 12 / 100) * math.pow(1 + rate/12/100, tenure) / (math.pow(1 + rate/12/100, tenure) - 1), 2) if rate > 0 else round(amount/tenure, 2)
                    _safe_insert({
                        "doctype": "EMI Schedule", "loan_application": loan_app, "loan_disbursement": disb,
                        "total_emis": tenure, "remaining_emis": _rand_int(1, tenure), "emi_amount": emi,
                        "disbursement_date": add_days(today(), -_rand_int(15, 90)),
                        "first_emi_date": add_months(today(), -_rand_int(1, 3)),
                    })
                    for emi_num in range(1, min(4, _rand_int(1, 6))):
                        _safe_insert({
                            "doctype": "Loan Repayment", "loan_application": loan_app, "customer": cust.name,
                            "amount": _rand_amount(5000, 50000),
                            "payment_date": add_days(add_months(today(), -emi_num), -_rand_int(1, 5)),
                            "payment_mode": random.choice(["NACH Auto-Debit", "UPI", "NEFT"]), "status": "Completed",
                        })
        print("  ✅ Loan Applications + Disbursements + Repayments created")

        for la in frappe.get_all("Loan Application", fields=["name", "customer_name", "loan_amount", "interest_rate", "tenure_months"]):
            _safe_insert({
                "doctype": "Sanction Letter", "loan_application": la.name, "customer_name": la.customer_name,
                "sanctioned_amount": la.loan_amount, "interest_rate": la.interest_rate,
                "tenure_months": la.tenure_months, "sanction_date": add_days(today(), -_rand_int(30, 120)),
                "status": "Accepted",
            })
        print("  ✅ Sanction Letters created")

        for la in frappe.get_all("Loan Application", fields=["name"])[:4]:
            _safe_insert({
                "doctype": "Credit Committee Decision", "naming_series": "CCD-.YYYY.-.####",
                "loan_application": la.name, "decision": "Approved",
                "decision_date": add_days(today(), -_rand_int(20, 60)),
            })
        print("  ✅ Credit Committee Decisions created")

    # ═════════════════════════════════════════════════════════════════════════
    # 5. INSURANCE
    # ═════════════════════════════════════════════════════════════════════════
    def _load_insurance():
        print("\n🛡️ INSURANCE MODULE")
        products = [
            {"insurance_product_name": "Term Life Cover", "product_type": "Life Insurance", "provider": "LIC of India",
             "min_sum_assured": 100000, "max_sum_assured": 10000000, "min_tenure_months": 12, "max_tenure_months": 360,
             "premium_frequency": "Yearly"},
            {"insurance_product_name": "Health Shield", "product_type": "Health Insurance", "provider": "Star Health",
             "min_sum_assured": 50000, "max_sum_assured": 5000000, "min_tenure_months": 12, "max_tenure_months": 12,
             "premium_frequency": "Yearly"},
            {"insurance_product_name": "Vehicle Insurance", "product_type": "Motor Insurance", "provider": "New India Assurance",
             "min_sum_assured": 50000, "max_sum_assured": 2000000, "min_tenure_months": 12, "max_tenure_months": 12,
             "premium_frequency": "Yearly"},
        ]
        for p in products:
            _safe_insert({"doctype": "Insurance Product", **p})
        print("  ✅ Insurance Products created")

        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"])
        for cust in customers[:4]:
            policy = _safe_insert({
                "doctype": "Insurance Policy", "customer": cust.name, "customer_name": cust.customer_name,
                "insurance_product": random.choice(products)["insurance_product_name"],
                "sum_assured": _rand_amount(100000, 10000000), "premium_amount": _rand_amount(5000, 50000),
                "start_date": add_days(today(), -_rand_int(100, 365)),
                "expiry_date": add_months(today(), _rand_int(6, 12)), "status": "Active",
            })
            if policy:
                _safe_insert({
                    "doctype": "Premium Payment", "policy": policy,
                    "premium_amount": _rand_amount(5000, 50000),
                    "payment_date": add_days(today(), -_rand_int(10, 90)),
                    "payment_mode": "NEFT", "status": "Paid",
                })
        print("  ✅ Insurance Policies + Premiums created")

    # ═════════════════════════════════════════════════════════════════════════
    # 6. INVESTMENTS
    # ═════════════════════════════════════════════════════════════════════════
    def _load_investments():
        print("\n📈 INVESTMENTS MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"])

        for cust in customers[:4]:
            _safe_insert({
                "doctype": "Investment Account", "customer": cust.name, "account_type": "Demat",
                "account_number": f"DMAT{random.randint(100000,999999)}",
                "depository": random.choice(["NSDL", "CDSL"]), "status": "Active",
            })
        print("  ✅ Investment Accounts created")

        for mf in [
            {"fund_name": "HDFC Top 100 Fund", "fund_type": "Equity", "fund_house": "HDFC Mutual Fund", "nav": _rand_amount(50, 500)},
            {"fund_name": "SBI Bluechip Fund", "fund_type": "Equity", "fund_house": "SBI Mutual Fund", "nav": _rand_amount(30, 300)},
            {"fund_name": "ICICI Prudential Value Discovery", "fund_type": "Equity", "fund_house": "ICICI Prudential MF", "nav": _rand_amount(80, 400)},
            {"fund_name": "Kotak Bond Fund", "fund_type": "Debt", "fund_house": "Kotak Mahindra MF", "nav": _rand_amount(100, 500)},
            {"fund_name": "Axis Liquid Fund", "fund_type": "Liquid", "fund_house": "Axis Mutual Fund", "nav": _rand_amount(1000, 5000)},
        ]:
            _safe_insert({"doctype": "Mutual Fund", **mf})
        print("  ✅ Mutual Funds created")

        for cust in customers[:3]:
            _safe_insert({
                "doctype": "Fixed Deposit", "customer": cust.name, "deposit_amount": _rand_amount(50000, 500000),
                "interest_rate": _rand_amount(5.5, 7.5), "tenure_months": _rand_int(6, 60),
                "deposit_date": add_days(today(), -_rand_int(30, 365)),
                "maturity_date": add_months(today(), _rand_int(1, 12)), "status": "Active",
            })
        print("  ✅ Fixed Deposits created")

        for g in [
            {"customer": customers[0].name, "goal_name": "Retirement Corpus", "target_amount": 5000000, "current_amount": 500000, "target_date": add_years(today(), 20)},
            {"customer": customers[1].name, "goal_name": "Child Education", "target_amount": 2000000, "current_amount": 300000, "target_date": add_years(today(), 10)},
        ]:
            _safe_insert({"doctype": "Investment Goal", **g})
        print("  ✅ Investment Goals created")

    # ═════════════════════════════════════════════════════════════════════════
    # 7. PORTFOLIO MANAGEMENT
    # ═════════════════════════════════════════════════════════════════════════
    def _load_portfolio():
        print("\n📊 PORTFOLIO MANAGEMENT MODULE")
        asset_classes_list = ["Equity", "Debt", "Gold", "Real Estate", "Cash", "Alternative Investments"]
        for a in asset_classes_list:
            _safe_insert({"doctype": "Asset Class", "asset_class_name": a, "risk_level": random.choice(["Low", "Medium", "High"])})
        print("  ✅ Asset Classes created")

        customers = frappe.get_all("Bizaxl Customer", fields=["name"])
        for cust in customers[:4]:
            for _ in range(random.randint(2, 4)):
                _safe_insert({
                    "doctype": "Portfolio Holding", "customer": cust.name,
                    "asset_class": random.choice(asset_classes_list),
                    "holding_name": f"Demo {random.choice(['Stock','Fund','Bond'])} {random.randint(1,100)}",
                    "invested_amount": _rand_amount(10000, 500000), "current_value": _rand_amount(10000, 500000),
                    "quantity": _rand_int(10, 1000), "purchase_date": add_days(today(), -_rand_int(30, 365)),
                })
        print("  ✅ Portfolio Holdings created")

        for cust in customers[:3]:
            _safe_insert({
                "doctype": "Financial Goal", "customer": cust.name,
                "goal_name": random.choice(["Buy a House", "World Trip", "Early Retirement", "Startup Fund"]),
                "target_amount": _rand_amount(1000000, 10000000), "current_savings": _rand_amount(50000, 500000),
                "target_date": add_years(today(), random.randint(3, 20)), "goal_type": "Long Term",
            })
        print("  ✅ Financial Goals created")

    # ═════════════════════════════════════════════════════════════════════════
    # 8. GOLD LOAN
    # ═════════════════════════════════════════════════════════════════════════
    def _load_gold_loan():
        print("\n🥇 GOLD LOAN MODULE")
        for a in [
            {"auctioneer_name": "Mumbai Gold Auctions", "contact_person": "Ramesh Shah", "contact_number": "9988776601",
             "commission_percentage": 2.0, "specialization": "Gold", "city": "Mumbai", "status": "Active"},
            {"auctioneer_name": "Chennai Bullion House", "contact_person": "Karthik Iyer", "contact_number": "9988776602",
             "commission_percentage": 1.5, "specialization": "Gold", "city": "Chennai", "status": "Active"},
        ]:
            _safe_insert({"doctype": "Auctioneer Register", "naming_series": "AUCTNR-.YYYY.-.####", **a})
        print("  ✅ Auctioneer Register created")

        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"])
        for cust in customers[:4]:
            _safe_insert({
                "doctype": "Vault Register", "customer_name": cust.customer_name, "branch": "Head Office - Mumbai",
                "total_items": _rand_int(1, 5), "total_weight": _rand_amount(10, 100),
                "vault_location": f"Vault-{random.choice(['A','B','C'])}-{random.randint(1,50)}", "status": "Active",
            })
        print("  ✅ Vault Register created")

        for cust in customers[:3]:
            item_value = _rand_amount(50000, 500000)
            weight = _rand_amount(10, 50)
            loan_amt = item_value * 0.75
            _safe_insert({
                "doctype": "Gold Pledge", "naming_series": "GP-.YYYY.-.####", "customer_name": cust.customer_name,
                "loan_amount": round(loan_amt, 2), "interest_rate": _rand_amount(6, 12),
                "tenure_months": _rand_int(6, 18), "interest_type": "Reducing",
                "total_gold_value": round(item_value, 2), "total_gross_weight": round(weight, 2),
                "total_net_weight": round(weight * 0.92, 2), "ltv_ratio": 75.00,
                "market_rate_per_gram": _rand_amount(4000, 6000),
                "valuation_date": add_days(today(), -_rand_int(10, 60)),
                "disbursement_date": add_days(today(), -_rand_int(5, 30)),
                "disbursed_amount": round(loan_amt, 2), "disbursement_mode": "NEFT",
                "maturity_date": add_months(today(), _rand_int(1, 12)), "status": "Active",
            })
        print("  ✅ Gold Pledges created")

    # ═════════════════════════════════════════════════════════════════════════
    # 9. VEHICLE LOAN
    # ═════════════════════════════════════════════════════════════════════════
    def _load_vehicle_loan():
        print("\n🚗 VEHICLE LOAN MODULE")
        for d in [
            {"dealer_name": "Mumbai Auto Centre", "city": "Mumbai", "contact_person": "Dinesh Joshi",
             "contact_number": "9988776631", "commission_rate": 2.0, "status": "Active"},
            {"dealer_name": "Chennai Car World", "city": "Chennai", "contact_person": "Suresh Babu",
             "contact_number": "9988776632", "commission_rate": 2.5, "status": "Active"},
        ]:
            _safe_insert({"doctype": "Dealer Master", "naming_series": "DLR-.YYYY.-.####", **d})
        print("  ✅ Dealer Masters created")

        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"])
        for i, cust in enumerate(customers[:3]):
            vehicle_cat = random.choice(["2 Wheeler", "4 Wheeler - Hatchback", "4 Wheeler - Sedan", "4 Wheeler - SUV"])
            otr = _rand_amount(80000, 1500000) if "2 Wheeler" in vehicle_cat else _rand_amount(500000, 2500000)
            down_pct = random.choice([10, 15, 20])
            _safe_insert({
                "doctype": "Vehicle Detail", "naming_series": "VH-.YYYY.-.####", "vehicle_category": vehicle_cat,
                "make": random.choice(["Maruti Suzuki", "Hyundai", "Honda", "Tata", "Toyota", "Bajaj"]),
                "model": f"Model {random.randint(2020, 2024)}", "manufacture_year": random.randint(2020, 2024),
                "condition": "New" if i == 0 else "Used - Certified",
                "otr_price": otr, "valuation_price": otr * 0.95, "agreed_price": otr * 0.93,
                "down_payment": otr * down_pct / 100,
                "registration_number": f"{random.choice(['MH','TN','KA','DL'])}-{random.randint(10,99)}-{random.choice(['AB','CD','EF','GH'])}{random.randint(1000,9999)}",
                "engine_number": f"ENG{random.randint(100000,999999)}",
                "chassis_number": f"CHS{random.randint(100000,999999)}",
                "fuel_type": random.choice(["Petrol", "Diesel", "Electric"]),
                "insurance_expiry": add_months(today(), _rand_int(1, 12)),
                "rc_hypothecation_status": random.choice(["Pending", "Submitted to RTO", "Endorsed"]), "status": "Active",
            })
        print("  ✅ Vehicle Details created")

        for _ in range(2):
            vehs = frappe.get_all("Vehicle Detail", limit=1)
            _safe_insert({
                "doctype": "Vehicle Repossession", "naming_series": "REPO-.YYYY.-.####",
                "vehicle": vehs[0].name if vehs else None,
                "customer_name": random.choice(["Default Borrower", "NPA Customer"]),
                "repossession_date": add_days(today(), -_rand_int(10, 60)),
                "repossession_reason": "NPA 90+ Days", "repossession_type": "Involuntary",
                "estimated_value": _rand_amount(200000, 800000), "recovery_cost": _rand_amount(10000, 50000),
                "storage_location": random.choice(["Branch Yard", "Third Party Yard"]),
                "inventory_condition": "Good", "status": "In Yard",
            })
        print("  ✅ Vehicle Repossessions created")

    # ═════════════════════════════════════════════════════════════════════════
    # 10. HOME LOAN
    # ═════════════════════════════════════════════════════════════════════════
    def _load_home_loan():
        print("\n🏠 HOME LOAN MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"])
        for cust in customers[:3]:
            _safe_insert({
                "doctype": "Property Detail", "naming_series": "PROP-.YYYY.-.####",
                "property_type": random.choice(["Apartment/Flat", "Independent House", "Villa"]),
                "property_address": f"{random.randint(1,100)} Main Road, {random.choice(['Andheri','Koramangala','Indiranagar','T Nagar'])}",
                "city": random.choice(["Mumbai", "Bangalore", "Chennai"]),
                "state": random.choice(["Maharashtra", "Karnataka", "Tamil Nadu"]),
                "pincode": str(random.randint(400001, 600001)),
                "built_up_area": _rand_amount(800, 2500), "agreed_value": _rand_amount(3000000, 15000000),
                "market_value": _rand_amount(3000000, 15000000), "title_deed_number": f"TD-{random.randint(10000,99999)}",
                "legal_status": "Clear Title", "construction_stage": random.choice(["Completed", "Finishing", "Roof"]),
            })
        print("  ✅ Property Details created")

        loan_apps_hl = frappe.get_all("Loan Application", filters={"loan_product": "Home Loan - DreamHome"}, limit=1)
        for loan_app in loan_apps_hl:
            for stage_num, stage in enumerate(["Land Purchase", "Foundation", "Construction Stage 1", "Construction Stage 2", "Finishing"]):
                _safe_insert({
                    "doctype": "Tranche Disbursement", "naming_series": "TR-.YYYY.-.####",
                    "loan_application": loan_app.name, "tranche_number": stage_num + 1,
                    "tranche_amount": _rand_amount(500000, 2000000), "tranche_purpose": stage,
                    "planned_date": add_months(today(), stage_num * 3),
                    "status": "Planned" if stage_num > 1 else "Disbursed",
                })
        print("  ✅ Tranche Disbursements created")

        _safe_insert({
            "doctype": "PMAY Subsidy", "naming_series": "PMAY-.YYYY.-.####",
            "applicant_name": customers[0].customer_name if customers else "Demo Applicant",
            "income_category": "MIG-I (Rs.6L-12L)", "is_first_home": 1, "eligible_for_clss": 1,
            "subsidy_amount": 235000, "principal_reduction": 235000, "subsidy_status": "Eligibility Checked",
        })
        print("  ✅ PMAY Subsidies created")

        all_loans = frappe.get_all("Loan Application", limit=1)
        if all_loans:
            _safe_insert({
                "doctype": "Legal Opinion", "naming_series": "LEGAL-OP-.YYYY.-.####",
                "loan_application": all_loans[0].name,
                "customer_name": customers[0].customer_name if customers else "Demo",
                "opinion_date": add_days(today(), -10), "advocate_name": "Adv. Rajesh Sharma",
                "title_clear": "Clear", "encumbrance_status": "Clear",
                "legal_opinion_status": "Favorable", "recommendation": "Approve",
            })
            _safe_insert({
                "doctype": "Engineer Certificate", "naming_series": "ENG-CERT-.YYYY.-.####",
                "loan_application": all_loans[0].name,
                "customer_name": customers[0].customer_name if customers else "Demo",
                "inspection_date": add_days(today(), -5), "engineer_name": "Er. Prakash Iyer",
                "current_stage": "Ground Floor", "percentage_complete": 45, "quality_check": "Good",
                "certified_stage": "Foundation", "stage_certified": 1, "certification_status": "Certified",
            })
        print("  ✅ Legal Opinions + Engineer Certificates created")

    # ═════════════════════════════════════════════════════════════════════════
    # 11. BUSINESS LOAN
    # ═════════════════════════════════════════════════════════════════════════
    def _load_business_loan():
        print("\n💼 BUSINESS LOAN MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"])
        for cust in customers[:3]:
            _safe_insert({
                "doctype": "Business Profile", "naming_series": "BIZ-.YYYY.-.####",
                "business_name": f"{cust.customer_name} Enterprises",
                "gstin": f"27{cust.customer_name[:3].upper()}{random.randint(1001,9999)}C1Z5",
                "udyam_number": f"UDYAM-{random.choice(['MH','TN','KA'])}-{random.randint(100000,999999)}",
                "business_type": random.choice(["Sole Proprietorship", "Partnership", "Private Limited"]),
                "business_vintage_years": _rand_int(2, 20),
                "industry": random.choice(["Manufacturing", "Trading", "Services", "IT/ITES"]),
                "annual_turnover": _rand_amount(500000, 50000000),
                "net_profit_last_year": _rand_amount(100000, 5000000),
                "business_address": f"{random.randint(1,100)} Business Street",
                "net_profit": _rand_amount(200000, 5000000), "interest_expense": _rand_amount(50000, 500000),
                "depreciation": _rand_amount(50000, 300000), "loan_principal_repayment": _rand_amount(100000, 1000000),
            })
        print("  ✅ Business Profiles created")

        loan_apps = frappe.get_all("Loan Application", fields=["name"], limit=3)
        for la in loan_apps:
            _safe_insert({
                "doctype": "Loan Covenant", "loan_application": la.name,
                "covenant_type": random.choice(["DSCR", "Current Ratio", "Debt Equity Ratio"]),
                "required_value": _rand_amount(1.25, 2.0), "frequency": "Quarterly",
            })
        print("  ✅ Loan Covenants created")

    # ═════════════════════════════════════════════════════════════════════════
    # 12. EDUCATION LOAN
    # ═════════════════════════════════════════════════════════════════════════
    def _load_education_loan():
        print("\n🎓 EDUCATION LOAN MODULE")
        for inst in [
            {"institution_name": "IIT Bombay", "institution_type": "University", "city": "Mumbai", "state": "Maharashtra",
             "recognition": "UGC/AICTE", "naac_grade": "A++"},
            {"institution_name": "IIM Ahmedabad", "institution_type": "Management School", "city": "Ahmedabad",
             "state": "Gujarat", "recognition": "AICTE", "naac_grade": "A+"},
            {"institution_name": "Christian Medical College", "institution_type": "Medical College", "city": "Vellore",
             "state": "Tamil Nadu", "recognition": "MCI", "naac_grade": "A"},
        ]:
            _safe_insert({"doctype": "Institution Master", "naming_series": "INST-.YYYY.-.####", **inst})
        print("  ✅ Institution Masters created")

        for inst in frappe.get_all("Institution Master", limit=2):
            _safe_insert({
                "doctype": "Course Detail", "course_name": random.choice(["B.Tech Computer Science", "MBA Finance", "MD General Medicine", "B.Sc Nursing"]),
                "institution": inst.name, "course_duration_months": _rand_int(24, 60),
                "total_fees": _rand_amount(200000, 2000000),
            })
        print("  ✅ Course Details created")

    # ═════════════════════════════════════════════════════════════════════════
    # 13. BNPL
    # ═════════════════════════════════════════════════════════════════════════
    def _load_bnpl():
        print("\n🛒 BNPL MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"], limit=4)
        for cust in customers:
            limit_amount = _rand_amount(5000, 500000)
            bnpl_limit = _safe_insert({
                "doctype": "BNPL Limit", "naming_series": "BNPL-LMT-.YYYY.-.####",
                "customer_name": cust.customer_name, "credit_limit": limit_amount,
                "used_amount": _rand_amount(0, limit_amount * 0.6),
                "available_limit": limit_amount * 0.4, "interest_rate": 24.0, "status": "Active",
            })
            if bnpl_limit:
                for _ in range(random.randint(1, 3)):
                    _safe_insert({
                        "doctype": "BNPL Transaction", "naming_series": "BNPL-TXN-.YYYY.-.####",
                        "bnpl_limit": bnpl_limit, "customer_name": cust.customer_name,
                        "merchant_name": random.choice(["Amazon", "Flipkart", "Myntra", "Swiggy", "Zomato"]),
                        "merchant_type": "E-commerce", "transaction_amount": _rand_amount(1000, 25000),
                        "tenor_months": random.choice([3, 6, 9]),
                        "transaction_date": add_days(today(), -_rand_int(1, 30)),
                        "status": "Active", "subvention_rate": 20.0,
                    })
        print("  ✅ BNPL Limits + Transactions created")

    # ═════════════════════════════════════════════════════════════════════════
    # 14. INVOICE FINANCE
    # ═════════════════════════════════════════════════════════════════════════
    def _load_invoice_finance():
        print("\n🧾 INVOICE FINANCE MODULE")
        for a in [
            {"anchor_name": "Tata Motors Ltd", "credit_limit": 50000000, "city": "Mumbai", "industry": "Automotive", "status": "Active"},
            {"anchor_name": "Infosys Technologies", "credit_limit": 100000000, "city": "Bangalore", "industry": "IT Services", "status": "Active"},
        ]:
            _safe_insert({"doctype": "Anchor Master", "naming_series": "ANCH-.YYYY.-.####", **a})
        print("  ✅ Anchor Masters created")

        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"], limit=3)
        anchors = frappe.get_all("Anchor Master", limit=1)
        for cust in customers:
            amount = _rand_amount(100000, 1000000)
            _safe_insert({
                "doctype": "Invoice Finance", "naming_series": "INV-.YYYY.-.####",
                "anchor": anchors[0].name if anchors else None, "supplier_name": cust.customer_name,
                "invoice_number": f"INV-{random.randint(10000,99999)}",
                "invoice_date": add_days(today(), -_rand_int(10, 60)),
                "invoice_amount": amount, "grn_number": f"GRN-{random.randint(10000,99999)}",
                "grn_verified": 1, "funding_status": "Funded",
                "disbursement_date": add_days(today(), -_rand_int(5, 30)),
                "disbursed_amount": round(amount * 0.85, 2), "due_date": add_days(today(), _rand_int(15, 90)),
            })
        print("  ✅ Invoice Finance created")

    # ═════════════════════════════════════════════════════════════════════════
    # 15. CHIT FUND
    # ═════════════════════════════════════════════════════════════════════════
    def _load_chit_fund():
        print("\n🏆 CHIT FUND MODULE")
        for group_num in range(1, 4):
            members = random.choice([15, 20, 25])
            value = members * _rand_amount(2000, 5000)
            _safe_insert({
                "doctype": "Chit Group", "naming_series": "CHIT-GRP-.YYYY.-.####",
                "chit_value": round(value, 2), "number_of_members": members,
                "monthly_subscription": round(value / members, 2), "duration_months": members,
                "foreman_commission": 5.0, "foreman_commission_amount": round(value * 0.05, 2),
                "start_date": add_months(today(), -_rand_int(1, 6)),
                "expected_end_date": add_months(today(), _rand_int(members - 6, members)),
                "status": "Active", "remarks": f"{members} member chit group #{group_num}",
            })
        print("  ✅ Chit Groups created")

        chit_groups = frappe.get_all("Chit Group", limit=2)
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"], limit=6)
        for cg in chit_groups:
            group = frappe.get_doc("Chit Group", cg.name)
            for i, cust in enumerate(customers[:min(5, int(group.number_of_members))]):
                _safe_insert({
                    "doctype": "Chit Subscriber", "chit_group": cg.name, "subscriber_name": cust.customer_name,
                    "subscriber_type": "Prized" if i == 0 else "Non-Prized",
                    "subscription_amount": group.monthly_subscription,
                    "total_paid": group.monthly_subscription * _rand_int(1, 4), "status": "Active",
                })
        for cg in chit_groups[:1]:
            for auction_no in range(1, 4):
                _safe_insert({
                    "doctype": "Chit Auction", "naming_series": "CHIT-AUC-.YYYY.-.####",
                    "chit_group": cg.name, "auction_number": auction_no,
                    "auction_date": add_months(today(), -auction_no + 1),
                    "winner_name": random.choice([c.customer_name for c in customers]) if customers else "Winner",
                    "bid_amount": _rand_amount(1000, 5000), "status": "Completed" if auction_no < 3 else "Scheduled",
                })
        print("  ✅ Chit Subscribers + Auctions created")

    # ═════════════════════════════════════════════════════════════════════════
    # 16. CONSUMER FINANCE
    # ═════════════════════════════════════════════════════════════════════════
    def _load_consumer_finance():
        print("\n📦 CONSUMER FINANCE MODULE")
        for r in [
            {"retailer_name": "Croma Electronics", "city": "Mumbai", "contact_number": "9988776641", "commission_rate": 3.0, "status": "Active"},
            {"retailer_name": "Vijay Sales", "city": "Mumbai", "contact_number": "9988776642", "commission_rate": 2.5, "status": "Active"},
            {"retailer_name": "Reliance Digital", "city": "Bangalore", "contact_number": "9988776643", "commission_rate": 3.0, "status": "Active"},
        ]:
            _safe_insert({"doctype": "Retailer Master", "naming_series": "RET-.YYYY.-.####", **r})
        print("  ✅ Retailer Masters created")

        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"], limit=3)
        for cust in customers:
            _safe_insert({
                "doctype": "POS Transaction", "naming_series": "POS-.YYYY.-.####",
                "customer": cust.customer_name, "retailer": "Croma Electronics",
                "product_category": random.choice(["AC", "TV", "Laptop", "Mobile", "Furniture"]),
                "transaction_amount": _rand_amount(10000, 100000), "tenor_months": random.choice([3, 6, 9, 12]),
                "transaction_date": add_days(today(), -_rand_int(1, 60)), "status": "Active",
            })
        print("  ✅ POS Transactions created")

    # ═════════════════════════════════════════════════════════════════════════
    # 17. COLLECTIONS
    # ═════════════════════════════════════════════════════════════════════════
    def _load_collections():
        print("\n💸 COLLECTIONS MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"], limit=4)
        for cust in customers:
            _safe_insert({
                "doctype": "NACH Mandate", "naming_series": "NACH-.YYYY.-.####",
                "customer": cust.name, "customer_name": cust.customer_name, "mandate_type": "Physical",
                "bank_account": frappe.get_value("Bank Account", {"customer": cust.name}),
                "maximum_amount": _rand_amount(10000, 100000),
                "start_date": add_days(today(), -_rand_int(30, 90)),
                "end_date": add_months(today(), _rand_int(6, 36)), "status": "Active",
            })

        loan_apps = frappe.get_all("Loan Application", fields=["name", "customer_name"], limit=5)
        for la in loan_apps:
            _safe_insert({
                "doctype": "Collection Record", "naming_series": "CL-.YYYY.-.####",
                "loan_application": la.name, "customer_name": la.customer_name,
                "collection_date": add_days(today(), -_rand_int(1, 15)),
                "amount_collected": _rand_amount(5000, 30000),
                "collection_mode": random.choice(["Cash", "UPI", "Bank Transfer", "NACH"]),
                "status": "Collected", "collection_officer": "Administrator",
            })

        for la in loan_apps[:2]:
            _safe_insert({
                "doctype": "NPA Classification", "naming_series": "NPA-.YYYY.-.####",
                "loan_application": la.name, "customer_name": la.customer_name,
                "npa_category": random.choice(["SMA-1", "SMA-2", "Sub-Standard"]),
                "outstanding_amount": _rand_amount(50000, 500000), "overdue_days": _rand_int(30, 180),
                "provision_percentage": random.choice([10, 15, 25, 40]),
                "classification_date": add_days(today(), -_rand_int(1, 30)), "status": "Active",
            })

        for la in loan_apps[:1]:
            _safe_insert({
                "doctype": "SARFAESI Case", "naming_series": "SARF-.YYYY.-.####",
                "loan_application": la.name, "customer_name": la.customer_name,
                "notice_date": add_days(today(), -_rand_int(30, 60)),
                "possession_date": add_days(today(), -_rand_int(10, 20)), "case_stage": "Notice Issued",
                "property_details": "Demo property under SARFAESI action", "status": "Active",
            })
        print("  ✅ Collections data created")

    # ═════════════════════════════════════════════════════════════════════════
    # 18. RISK & COMPLIANCE
    # ═════════════════════════════════════════════════════════════════════════
    def _load_risk_compliance():
        print("\n🛡️ RISK & COMPLIANCE MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"], limit=4)
        for cust in customers:
            _safe_insert({
                "doctype": "AML Screening", "naming_series": "AML-.YYYY.-.####",
                "customer_name": cust.customer_name, "screening_type": "Onboarding",
                "screening_date": add_days(today(), -_rand_int(10, 60)),
                "match_found": 0, "risk_score": _rand_int(1, 50), "status": "Cleared",
            })
        for cust in customers[:2]:
            _safe_insert({
                "doctype": "Fraud Alert", "naming_series": "FA-.YYYY.-.####",
                "customer_name": cust.customer_name,
                "alert_type": random.choice(["Unusual Transaction", "KYC Mismatch", "Multiple Applications"]),
                "severity": random.choice(["Medium", "Low"]),
                "description": f"Suspicious activity detected for {cust.customer_name}",
                "status": "Under Review",
            })
        for rt in ["CRILC", "FPC Report", "PSL Report"]:
            _safe_insert({
                "doctype": "Regulatory Report", "naming_series": "REGREP-.YYYY.-.####",
                "report_name": f"{rt} - {add_months(today(), -1)}", "report_type": rt,
                "reporting_period": "Monthly", "period_start": add_months(today(), -1),
                "period_end": today(), "status": "Ready",
            })
        print("  ✅ Risk & Compliance data created")

    # ═════════════════════════════════════════════════════════════════════════
    # 19. ACCOUNTING
    # ═════════════════════════════════════════════════════════════════════════
    def _load_accounting():
        print("\n📊 ACCOUNTING MODULE")
        try:
            gl = frappe.get_single("GL Settings")
            gl.company = frappe.get_all("Company", limit=1)[0].name if frappe.get_all("Company") else "Demo Company"
            gl.default_currency = "INR"
            gl.auto_post_to_gl = 1
            gl.auto_accrue_interest = 1
            gl.accrual_frequency = "Monthly"
            gl.save(ignore_permissions=True)
            print("  ✅ GL Settings updated")
        except Exception:
            print("  ⚠️ GL Settings - ERPNext Company needed, configured manually")

        for r in [
            {"rule_name": "Standard Asset Provision", "npa_category": "Standard", "provision_percentage": 0.40},
            {"rule_name": "Sub-Standard Provision", "npa_category": "Sub-Standard", "provision_percentage": 15.00},
            {"rule_name": "Doubtful Provision", "npa_category": "Doubtful", "provision_percentage": 25.00},
            {"rule_name": "Loss Asset Provision", "npa_category": "Loss", "provision_percentage": 100.00},
        ]:
            _safe_insert({"doctype": "Provisioning Rule", **r})

        for branch in frappe.get_all("Branch Master", limit=3):
            _safe_insert({
                "doctype": "Fund Account", "naming_series": "FA-.YYYY.-.####", "branch": branch.name,
                "fund_name": f"Disbursement Fund - {branch.name}", "fund_type": "Disbursement",
                "current_balance": _rand_amount(1000000, 10000000), "currency": "INR",
            })

        _safe_insert({
            "doctype": "Co-lending Partnership", "partner_name": "State Bank of India", "partner_type": "Bank",
            "partnership_date": add_days(today(), -_rand_int(30, 180)), "co_lending_ratio": 80.0, "status": "Active",
        })
        print("  ✅ Accounting data created")

    # ═════════════════════════════════════════════════════════════════════════
    # 20. CREDIT MANAGEMENT
    # ═════════════════════════════════════════════════════════════════════════
    def _load_credit_mgmt():
        print("\n📋 CREDIT MANAGEMENT MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"], limit=4)
        for cust in customers:
            _safe_insert({
                "doctype": "Credit Report", "customer": cust.name,
                "bureau_name": random.choice(["CIBIL", "Experian", "CRIF"]),
                "credit_score": _rand_int(600, 850), "report_date": add_days(today(), -_rand_int(10, 60)),
                "total_accounts": _rand_int(2, 10), "active_loans": _rand_int(0, 4), "status": "Fetched",
            })
            _safe_insert({
                "doctype": "Credit Score History", "customer": cust.name, "bureau": "CIBIL",
                "credit_score": _rand_int(600, 850), "score_date": add_months(today(), -_rand_int(1, 6)),
            })
            _safe_insert({
                "doctype": "Credit Goal", "customer": cust.name, "target_score": _rand_int(750, 850),
                "current_score": _rand_int(600, 750), "target_date": add_years(today(), 1),
                "goal_status": "In Progress",
            })
        print("  ✅ Credit Management data created")

    # ═════════════════════════════════════════════════════════════════════════
    # 21. MICROFINANCE
    # ═════════════════════════════════════════════════════════════════════════
    def _load_microfinance():
        print("\n🤝 MICROFINANCE MODULE")
        for cn in ["Koramangala Center", "Indiranagar Center", "Whitefield Center"][:3]:
            center = _safe_insert({
                "doctype": "MFI Center", "naming_series": "MFI-C-.YYYY.-.####", "center_name": cn,
                "center_meeting_day": random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
                "area": random.choice(["Urban", "Semi-Urban", "Rural"]),
                "city": "Bangalore", "state": "Karnataka", "status": "Active",
            })
            if center:
                group = _safe_insert({
                    "doctype": "JLG Group", "naming_series": "JLG-.YYYY.-.####",
                    "group_name": f"Group of {cn}", "center": center,
                    "formation_date": add_months(today(), -_rand_int(3, 12)),
                    "group_leader": "Demo Leader", "status": "Active",
                })
                if group:
                    for mn in ["Lakshmi", "Radha", "Geetha"][:3]:
                        _safe_insert({
                            "doctype": "MFI Member", "naming_series": "MFI-M-.YYYY.-.####",
                            "member_name": mn, "jlg_group": group, "center": center,
                            "mobile_number": f"+91{random.randint(6000000000,9999999999)}",
                            "household_income": _rand_amount(5000, 20000),
                            "loan_amount": _rand_amount(5000, 50000),
                            "outstanding_amount": _rand_amount(1000, 40000), "status": "Active",
                        })
        print("  ✅ Microfinance data created")

    # ═════════════════════════════════════════════════════════════════════════
    # 22. NBFC LENDING
    # ═════════════════════════════════════════════════════════════════════════
    def _load_nbfc():
        print("\n🏛️ NBFC LENDING MODULE")
        customers = frappe.get_all("Bizaxl Customer", fields=["name", "customer_name"], limit=3)
        for cust in customers:
            _safe_insert({
                "doctype": "NBFC Loan Application", "naming_series": "NBFC-LA-.YYYY.-.####",
                "customer": cust.name, "customer_name": cust.customer_name,
                "loan_amount": _rand_amount(1000000, 10000000), "interest_rate": _rand_amount(10, 18),
                "tenure_months": _rand_int(12, 60), "status": "Under Review", "purpose": "Business Expansion",
            })
        print("  ✅ NBFC data created")

    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTE ALL
    # ═══════════════════════════════════════════════════════════════════════════
    print("=" * 60)
    print("📦 BIZAXL FINANCE — DEMO DATA LOADER")
    print("=" * 60)

    _load_foundation()
    _load_customers()
    _load_banking()
    _load_loans()
    _load_insurance()
    _load_investments()
    _load_portfolio()
    _load_gold_loan()
    _load_vehicle_loan()
    _load_home_loan()
    _load_business_loan()
    _load_education_loan()
    _load_bnpl()
    _load_invoice_finance()
    _load_chit_fund()
    _load_consumer_finance()
    _load_collections()
    _load_risk_compliance()
    _load_accounting()
    _load_credit_mgmt()
    _load_microfinance()
    _load_nbfc()

    print("\n" + "=" * 60)
    print("✅ DEMO DATA LOADING COMPLETE!")
    print("=" * 60)


# ── Entry point ─────────────────────────────────────────────────────────────────
# For exec() in Frappe console: always call load_demo_data()
# (no __name__ guard — exec() doesn't set __name__ to "__main__")
# For bench execute: the function is imported and called explicitly.
# Double-execution is harmless (ignore_if_duplicate skips duplicates).
load_demo_data()
