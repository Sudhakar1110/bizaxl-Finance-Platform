"""
Bizaxl Finance — Fix Module & DocType Mappings
================================================
Purpose: Fix "Module X not found" errors and orphan DocType deletion during migration.

The problem chain:
1. DocType JSON files have module: "Foundation", "Customer Management", etc.
2. Module Defs exist in DB but with wrong app_name (e.g. from a different app)
3. Migration can't resolve module -> deletes DocTypes as "orphaned"
4. Demo data script then finds DocTypes don't exist

Usage:
    bench --site your-site console
    exec(open("../apps/bizaxl_finance/bizaxl_finance/fix_modules.py").read())

Then:
    bench --site your-site migrate   # No orphan deletions now!
    bench --site your-site console
    exec(open("../apps/bizaxl_finance/bizaxl_finance/load_demo_data.py").read())
"""

import frappe
import os
import json

# Module names from fixtures/module_def.json
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


def fix_modules():
    print("=" * 60)
    print("📦 BIZAXL FINANCE — FIX MODULE & DOCTYPE MAPPINGS")
    print("=" * 60)

    # ── Step 1: Fix all Module Defs ────────────────────────────────────────
    print("\n🔧 Step 1/3: Fixing Module Def app_name mappings...")
    fixed_modules = 0
    created_modules = 0

    for mod_name in ALL_MODULE_NAMES:
        if frappe.db.exists("Module Def", mod_name):
            # Fix app_name if wrong
            current_app = frappe.db.get_value("Module Def", mod_name, "app_name")
            if current_app != APP_NAME:
                frappe.db.set_value("Module Def", mod_name, "app_name", APP_NAME)
                print(f"  🔄 Fixed app_name: {mod_name} ({current_app} → {APP_NAME})")
                fixed_modules += 1
            else:
                print(f"  ✅ Correct: {mod_name} → {APP_NAME}")
        else:
            # Create missing Module Def
            doc = frappe.get_doc({
                "doctype": "Module Def",
                "module_name": mod_name,
                "app_name": APP_NAME,
                "custom": 1,
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✅ Created: {mod_name}")
            created_modules += 1

    frappe.db.commit()
    print(f"\n📊 Module Def summary: {created_modules} created, {fixed_modules} fixed")

    # ── Step 2: Fix DocType module references ──────────────────────────────
    print("\n🔧 Step 2/3: Fixing DocType module references in database...")
    base_path = frappe.get_app_path(APP_NAME)

    # Discover all DocType JSONs
    doctype_jsons = {}
    for root, dirs, files in os.walk(base_path):
        if "doctype" in root.split(os.sep):
            for f in files:
                if f.endswith(".json") and f != "__init__.py":
                    doctype_path = os.path.join(root, f)
                    try:
                        with open(doctype_path) as fh:
                            data = json.load(fh)
                        if data.get("doctype") == "DocType":
                            dt_name = data.get("name")
                            dt_module = data.get("module")
                            if dt_name and dt_module:
                                doctype_jsons[dt_name] = dt_module
                    except Exception:
                        pass

    print(f"  Found {len(doctype_jsons)} DocType definitions in JSON files")

    # Update tabDocType records
    fixed_dt_count = 0
    for dt_name, expected_module in doctype_jsons.items():
        if frappe.db.exists("DocType", dt_name):
            current_module = frappe.db.get_value("DocType", dt_name, "module")
            if current_module != expected_module:
                frappe.db.set_value("DocType", dt_name, "module", expected_module)
                print(f"  🔄 Fixed {dt_name}: module '{current_module}' → '{expected_module}'")
                fixed_dt_count += 1

    frappe.db.commit()
    print(f"  Fixed {fixed_dt_count} DocType module references")

    # ── Step 3: Clear cache ────────────────────────────────────────────────
    print("\n🔧 Step 3/3: Clearing Frappe cache...")
    frappe.clear_cache()
    print("  ✅ Cache cleared")

    print("\n" + "=" * 60)
    print("✅ ALL FIXES COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Exit console (Ctrl+D)")
    print("  2. Run: bench --site your-site migrate")
    print("     (No orphan deletions expected now!)")
    print("  3. Run: bench --site your-site clear-cache")
    print("  4. Run demo data script again")


if __name__ == "__main__":
    fix_modules()

# For exec() in Frappe console
fix_modules()
