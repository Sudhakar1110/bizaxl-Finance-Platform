"""
Fix Integration Settings DocType.

Creates the Integration Settings single record in the database
so the workspace link works. Uses frappe.db.set_single_value()
to bypass module validation issues.

Run via bench console:
    exec(open("../apps/bizaxl_finance/bizaxl_finance/fix_integration_settings.py").read())
"""

import frappe
import json
import os


def fix():
    print("=" * 60)
    print("Fixing Integration Settings and Module Def...")
    print("=" * 60)

    base_dir = frappe.get_app_path("bizaxl_finance")
    doctype_name = "Integration Settings"

    # Step 1: Create DocType definition (if missing)
    json_path = os.path.join(base_dir, "integrations", "doctype", "integration_settings", "integration_settings.json")

    if not os.path.exists(json_path):
        print(f"❌ JSON file not found at: {json_path}")
        return

    if not frappe.db.exists("DocType", doctype_name):
        frappe.flags.in_import = True
        try:
            with open(json_path) as f:
                data = json.load(f)

            doc = frappe.get_doc(data)
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"✅ Created DocType: {doctype_name}")
        except Exception as e:
            frappe.db.rollback()
            print(f"❌ Failed to create DocType: {str(e)}")
            return
        finally:
            frappe.flags.in_import = False
    else:
        print(f"⏭️ DocType '{doctype_name}' already exists in database")

    # Step 2: Create single record using raw DB insert (bypasses meta validation)
    try:
        frappe.db.set_single_value(doctype_name, "scorecard_enabled", 0)
        frappe.db.commit()
        print(f"✅ Single record for '{doctype_name}' created in database")
    except Exception as e:
        frappe.db.rollback()
        print(f"❌ Failed to create single record: {str(e)}")

    print("=" * 60)
    print("Done! Run migration now - it should work cleanly.")
    print("=" * 60)


fix()
