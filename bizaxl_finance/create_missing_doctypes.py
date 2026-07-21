"""
Run this script from bench console to force-create 9 DocTypes directly in the DB.

Usage:
    bench --site your-site console
    exec(open("../apps/bizaxl_finance/bizaxl_finance/create_missing_doctypes.py").read())
"""

import frappe, json, os


def create_doctype_from_json(base_dir, doctype_name, relative_path):
    """Read a DocType JSON file and create it in the database"""
    full_path = os.path.join(base_dir, relative_path)

    if not os.path.exists(full_path):
        return f"SKIP: File not found: {full_path}"

    with open(full_path) as f:
        data = json.load(f)

    # Check if already exists
    if frappe.db.exists("DocType", doctype_name):
        return f"SKIP: Already exists: {doctype_name}"

    try:
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return f"OK: Created: {doctype_name}"
    except Exception as e:
        frappe.db.rollback()
        return f"FAIL: {doctype_name} - {str(e)}"


def run():
    base_dir = frappe.get_app_path("bizaxl_finance")

    doctypes_to_create = [
        ("Sanction Letter", "loans/doctype/sanction_letter/sanction_letter.json"),
        ("EMI Schedule", "loans/doctype/emi_schedule/emi_schedule.json"),
        ("Rate Reset Log", "loans/doctype/rate_reset_log/rate_reset_log.json"),
        ("Prepayment Request", "loans/doctype/prepayment_request/prepayment_request.json"),
        ("Loan Restructure", "loans/doctype/loan_restructure/loan_restructure.json"),
        ("Write-off", "collections/doctype/write_off/write_off.json"),
        ("Insurance Bundle Tracker", "insurance/doctype/insurance_bundle_tracker/insurance_bundle_tracker.json"),
        ("Chit ROC Return", "chit_fund/doctype/chit_roc_return/chit_roc_return.json"),
        ("Personal Loan Application", "loans/doctype/personal_loan_application/personal_loan_application.json"),
    ]

    print("=" * 60)
    print("Creating 9 missing DocTypes in database...")
    print("=" * 60)

    results = []
    for doctype_name, relative_path in doctypes_to_create:
        result = create_doctype_from_json(base_dir, doctype_name, relative_path)
        results.append(result)
        print(result)

    print("=" * 60)
    ok = [r for r in results if r.startswith("OK")]
    skip = [r for r in results if r.startswith("SKIP")]
    fail = [r for r in results if r.startswith("FAIL")]
    print(f"Created: {len(ok)}, Already existed: {len(skip)}, Failed: {len(fail)}")
    print("=" * 60)


run()
