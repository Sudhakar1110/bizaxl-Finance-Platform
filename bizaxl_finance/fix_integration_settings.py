"""
Fix Integration Settings DocType.

This script creates the Integration Settings DocType definition
and its initial Single record in the database.

Run via bench console:
    exec(open("../apps/bizaxl_finance/bizaxl_finance/fix_integration_settings.py").read())
"""

import frappe
import json
import os


def fix():
    print("=" * 60)
    print("Fixing Integration Settings DocType...")
    print("=" * 60)

    base_dir = frappe.get_app_path("bizaxl_finance")
    json_path = os.path.join(base_dir, "integrations", "doctype", "integration_settings", "integration_settings.json")

    if not os.path.exists(json_path):
        print(f"❌ JSON file not found at: {json_path}")
        return

    # Step 1: Create DocType definition
    doctype_name = "Integration Settings"
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

    # Step 2: Create single record if it doesn't exist
    try:
        settings = frappe.get_single(doctype_name)
        if not settings.get("__islocal"):
            print(f"⏭️ Single record for '{doctype_name}' already exists")
        else:
            settings.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"✅ Created single record for {doctype_name}")
    except Exception as e:
        frappe.db.rollback()
        print(f"❌ Failed to create single record: {str(e)}")

    print("=" * 60)
    print("Done! Integration Settings should now be accessible.")
    print("=" * 60)


fix()
