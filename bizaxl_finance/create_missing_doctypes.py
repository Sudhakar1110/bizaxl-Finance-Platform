"""
Run this script from bench console to force-create 9 DocTypes directly in the DB.
These DocTypes exist as JSON files on disk but Frappe's migration can't create them
because of module initialization ordering.

Usage:
    bench --site your-site console
    exec(open("../apps/bizaxl_finance/bizaxl_finance/create_missing_doctypes.py").read())
"""

import frappe, json, os

DOCTYPES_TO_CREATE = [
    # (doctype_name, json_path)
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

BASE_DIR = frappe.get_app_path("bizaxl_finance")

def create_doctype_from_json(doctype_name, relative_path):
    """Read a DocType JSON file and create it in the database"""
    full_path = os.path.join(BASE_DIR, relative_path)
    
    if not os.path.exists(full_path):
        return f"❌ File not found: {full_path}"
    
    with open(full_path) as f:
        data = json.load(f)
    
    # Check if already exists
    if frappe.db.exists("DocType", doctype_name):
        return f"⏭️ Already exists: {doctype_name}"
    
    try:
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return f"✅ Created: {doctype_name}"
    except Exception as e:
        frappe.db.rollback()
        return f"❌ Failed: {doctype_name} - {str(e)}"

def run():
    print("=" * 60)
    print("Creating 9 missing DocTypes in database...")
    print("=" * 60)
    
    results = []
    for doctype_name, relative_path in DOCTYPES_TO_CREATE:
        result = create_doctype_from_json(doctype_name, relative_path)
        results.append(result)
        print(result)
    
    print("=" * 60)
    success = [r for r in results if r.startswith("✅")]
    skipped = [r for r in results if r.startswith("⏭️")]
    failed = [r for r in results if r.startswith("❌")]
    print(f"Created: {len(success)}, Already existed: {len(skipped)}, Failed: {len(failed)}")
    print("=" * 60)
    
    if failed:
        print("\n❌ Failures detected. Run this command to retry individually:")
        for f_result in failed:
            name = f_result.split(":")[1].split("-")[0].strip()
            print(f"  python -c \"... create {name} ...\"")

if __name__ == "__main__":
    run()
