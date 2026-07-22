import frappe
from frappe import _
import json

# ── DocType Installer (browser-accessible) ─────────────────────────────────

@frappe.whitelist()
def install_all_doctypes():
    """Install all missing bizaxl_finance DocTypes.

    Call this from your browser via:
        https://finance.bizaxl.org/api/method/bizaxl_finance.api.install_all_doctypes

    Or visit the web UI at:
        https://finance.bizaxl.org/install-doctypes
    """
    # Only administrators can run this
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Only System Manager can install DocTypes", frappe.PermissionError)

    from bizaxl_finance.install_all_doctypes import run_and_return_results
    return run_and_return_results()


@frappe.whitelist()
def check_doctype_status():
    """Check which bizaxl_finance DocTypes are already installed vs missing.

    Returns counts and lists of installed/missing doctypes.
    Use this to preview before installing.
    """
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Only System Manager can check DocType status", frappe.PermissionError)

    base_dir = frappe.get_app_path("bizaxl_finance")
    from bizaxl_finance.install_all_doctypes import discover_doctype_paths

    doctype_list = discover_doctype_paths(base_dir)
    total = len(doctype_list)
    installed = []
    missing = []

    for doctype_name, rel_path in doctype_list:
        if frappe.db.exists("DocType", doctype_name):
            installed.append(doctype_name)
        else:
            missing.append(doctype_name)

    return {
        "total": total,
        "installed_count": len(installed),
        "installed": installed,
        "missing_count": len(missing),
        "missing": missing,
    }


# ── Comprehensive Fix: Modules + Workspace + Cache ─────────────────────────

@frappe.whitelist()
def fix_modules_and_workspace():
    """Fix Module Defs, DocType modules, recreate Workspace, and clear cache.

    Call from browser:
        https://finance.bizaxl.org/api/method/bizaxl_finance.api.fix_modules_and_workspace
    """
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Only System Manager can run this fix", frappe.PermissionError)

    import os

    results = {"modules_fixed": 0, "modules_created": 0, "doctype_module_fixes": 0, "workspace": False, "workspace_cards": 0, "workspace_links": 0, "errors": []}

    # ── 1. Fix Module Defs ──────────────────────────────────────────────────
    ALL_MODULE_NAMES = [
        "Bizaxl Finance", "Customer Management", "Banking", "Payments",
        "Investments", "Loans", "Insurance", "Credit Management",
        "Portfolio Management", "Foundation", "NBFC Lending", "Gold Loan",
        "Microfinance", "Vehicle Loan", "Home Loan", "Business Loan",
        "Education Loan", "BNPL", "Invoice Finance", "Chit Fund",
        "Consumer Finance", "Collections", "Risk Compliance",
        "Risk & Compliance", "Accounting",
    ]
    APP_NAME = "bizaxl_finance"

    for mod_name in ALL_MODULE_NAMES:
        if frappe.db.exists("Module Def", mod_name):
            current_app = frappe.db.get_value("Module Def", mod_name, "app_name")
            if current_app != APP_NAME:
                frappe.db.set_value("Module Def", mod_name, "app_name", APP_NAME)
                results["modules_fixed"] += 1
        else:
            try:
                doc = frappe.get_doc({
                    "doctype": "Module Def",
                    "module_name": mod_name,
                    "app_name": APP_NAME,
                    "custom": 1,
                })
                doc.insert(ignore_permissions=True)
                results["modules_created"] += 1
            except Exception as e:
                results["errors"].append(f"Module {mod_name}: {str(e)}")

    # ── Special case: Integrations must always belong to Frappe core ──────
    if frappe.db.exists("Module Def", "Integrations"):
        current_app = frappe.db.get_value("Module Def", "Integrations", "app_name")
        if current_app != "frappe":
            frappe.db.set_value("Module Def", "Integrations", "app_name", "frappe")
            results["modules_fixed"] += 1

    frappe.db.commit()

    # ── 2. Fix DocType module references ───────────────────────────────────
    base = frappe.get_app_path(APP_NAME)
    for root, dirs, files in os.walk(base):
        if "doctype" not in root.split(os.sep):
            continue
        for f in files:
            if not f.endswith(".json") or f == "__init__.py":
                continue
            try:
                with open(os.path.join(root, f)) as fh:
                    data = json.load(fh)
                if data.get("doctype") != "DocType":
                    continue
                dt_name = data.get("name")
                expected_module = data.get("module")
                if dt_name and expected_module and frappe.db.exists("DocType", dt_name):
                    current = frappe.db.get_value("DocType", dt_name, "module")
                    if current != expected_module:
                        frappe.db.set_value("DocType", dt_name, "module", expected_module)
                        results["doctype_module_fixes"] += 1
            except Exception:
                pass

    frappe.db.commit()

    # ── 3. Recreate Workspace using ORM (bypasses all validation) ──────────
    results["workspace"] = False
    try:
        fixture_path = os.path.join(base, "workspace", "bizaxl_finance", "bizaxl_finance.json")
        if not os.path.exists(fixture_path):
            results["errors"].append(f"Fixture not found: {fixture_path}")
        else:
            with open(fixture_path) as f:
                fixture = json.load(f)
            
            # Delete old workspace
            if frappe.db.exists("Workspace", "Bizaxl Finance"):
                frappe.get_doc("Workspace", "Bizaxl Finance").delete()
                frappe.db.commit()
            
            # Build new workspace doc
            doc_data = {
                "doctype": "Workspace",
                "name": "Bizaxl Finance",
                "title": "Bizaxl Finance",
                "module": "Bizaxl Finance",
                "label": "Bizaxl Finance",
                "icon": "credit-card",
                "is_hidden": 0,
                "is_standard": 0,
                "is_default": 1,
                "public": 1,
                "sequence_id": 1.0,
                "content": fixture["content"],
            }
            
            ws = frappe.get_doc(doc_data)
            
            # Add all links from fixture
            for link in fixture.get("links", []):
                ws.append("links", {
                    "type": link.get("type", ""),
                    "label": link.get("label", ""),
                    "link_to": link.get("link_to", ""),
                    "link_type": link.get("link_type", ""),
                    "hidden": link.get("hidden", 0),
                    "is_query_report": link.get("is_query_report", 0),
                    "onboard": link.get("onboard", 0),
                    "dependencies": link.get("dependencies", ""),
                })
            
            # Insert with ALL bypass flags
            ws.flags.ignore_links = True
            original_dev_mode = frappe.conf.developer_mode
            try:
                frappe.conf.developer_mode = 0
                ws.insert(ignore_permissions=True, ignore_if_duplicate=True)
                frappe.db.commit()
            finally:
                frappe.conf.developer_mode = original_dev_mode
            
            # Verify
            if frappe.db.exists("Workspace", "Bizaxl Finance"):
                ws_check = frappe.get_doc("Workspace", "Bizaxl Finance")
                results["workspace"] = True
                results["workspace_cards"] = len(json.loads(ws_check.content))
                results["workspace_links"] = len(ws_check.links)
    except Exception as e:
        results["errors"].append(f"Workspace: {str(e)}")

    # ── 4. Clear Cache ─────────────────────────────────────────────────────
    frappe.cache().delete_key("bootinfo")
    frappe.cache().delete_value("workspace:data:Bizaxl Finance")
    frappe.clear_cache()

    results["success"] = len(results["errors"]) == 0
    return results


def _fix_integrations_module():
    """Standalone fix — reset Integrations Module Def to Frappe core.

    Can be run via terminal (no browser needed):
        bench --site finance.bizaxl.org execute bizaxl_finance.api._fix_integrations_module

    Or via browser URL:
        https://finance.bizaxl.org/api/method/bizaxl_finance.api.reset_integrations_module
    """
    if frappe.db.exists("Module Def", "Integrations"):
        current = frappe.db.get_value("Module Def", "Integrations", "app_name")
        if current != "frappe":
            frappe.db.set_value("Module Def", "Integrations", "app_name", "frappe")
            frappe.db.commit()
            print(f"✅ Integrations Module Def: '{current}' → 'frappe'")
        else:
            print("✅ Integrations Module Def already has app_name='frappe'")

        # Clean up partially-created core DocTypes from previous crashed migrations
        # These DocTypes were orphaned+deleted, then partially recreated with wrong module
        BROKEN_DOCTYPES = [
            "Google Contacts", "Google Calendar", "Webhook", "Webhook Header",
            "Social Login Key", "OAuth Client Role", "OAuth Provider Settings",
            "Push Notification Settings", "Google Settings", "Google Drive",
            "Dropbox Settings", "LDAP Settings", "Token Cache",
            "LDAP Group Mapping", "Connected App", "Slack Webhook URL",
            "Query Parameters", "S3 Backup Settings",
        ]
        deleted = 0
        for dt in BROKEN_DOCTYPES:
            if frappe.db.exists("DocType", dt):
                try:
                    frappe.delete_doc("DocType", dt, ignore_on_trash=True, force=True)
                    print(f"  🗑️ Deleted broken DocType: {dt}")
                    deleted += 1
                except Exception:
                    frappe.db.sql(f"DELETE FROM `tabDocType` WHERE `name` = %s", dt)
                    frappe.db.sql(f"DROP TABLE IF EXISTS `tab{dt.replace(' ', '_')}`")
                    print(f"  🗑️ Force-deleted broken DocType: {dt}")
                    deleted += 1

        frappe.db.commit()

        # Clear ALL caches so nothing stale remains
        frappe.clear_cache()
        frappe.cache().delete_key("bootinfo")

        if deleted:
            print(f"✅ Cleaned up {deleted} broken DocTypes — run migrate now!")
        else:
            print("✅ No broken DocTypes found — ready for migrate!")
        return True
    else:
        print("⚠️ Integrations Module Def not found in database")
        return False


@frappe.whitelist()
def reset_integrations_module():
    """Reset the Integrations Module Def back to Frappe core.

    Call this once from your browser:
        https://finance.bizaxl.org/api/method/bizaxl_finance.api.reset_integrations_module

    If the Integrations module has app_name=bizaxl_finance (from a previous
    fixture load), this resets it to app_name=frappe so Frappe core DocTypes
    (Webhook, Google Calendar, etc.) are not deleted as orphaned during migrate.
    """
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Only System Manager can run this", frappe.PermissionError)

    result = {"fixed": False, "message": "", "current_app": ""}

    if frappe.db.exists("Module Def", "Integrations"):
        current_app = frappe.db.get_value("Module Def", "Integrations", "app_name")
        result["current_app"] = current_app

        if current_app != "frappe":
            frappe.db.set_value("Module Def", "Integrations", "app_name", "frappe")
            frappe.db.commit()
            frappe.clear_cache()
            result["fixed"] = True
            result["message"] = f"✅ Integrations Module Def reset from '{current_app}' → 'frappe'"
        else:
            result["fixed"] = True
            result["message"] = "✅ Integrations Module Def already has app_name='frappe'. No change needed."
    else:
        result["message"] = "⚠️ Integrations Module Def does not exist in database!"

    return result


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


# ── Portal APIs ─────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def submit_loan_application_from_portal(loan_product, loan_amount, tenure_months, interest_rate, purpose=""):
    """Submit loan application from the customer portal"""
    customer = frappe.db.get_value("Bizaxl Customer", {"email": frappe.session.user}, "name")
    if not customer:
        return {"error": "Customer profile not found"}
    
    loan = frappe.get_doc({
        "doctype": "Loan Application",
        "customer": customer,
        "loan_product": loan_product,
        "loan_amount": frappe.utils.flt(loan_amount),
        "tenure_months": int(tenure_months),
        "interest_rate": frappe.utils.flt(interest_rate),
        "purpose": purpose,
        "status": "Draft",
    })
    loan.insert(ignore_permissions=True)
    
    frappe.get_doc({
        "doctype": "Customer Communication",
        "customer": customer,
        "subject": "Loan Application Submitted",
        "message_body": f"Your loan application for ₹{loan.loan_amount:,.2f} has been submitted.",
        "channel": "App Notification",
        "communication_type": "Notification",
        "status": "Sent",
    }).insert(ignore_permissions=True)
    
    return {"success": True, "loan_id": loan.name, "message": "Application submitted"}


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
