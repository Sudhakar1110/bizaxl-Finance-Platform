"""
Fix Integration Settings DocType.

Creates:
1. 'Bizaxl Finance' Module Def (if missing)
2. Integration Settings DocType definition (if missing)
3. Integration Settings single record (if missing)

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
    doctype_name = "Integration Settings"

    # Step 0: Ensure 'Bizaxl Finance' Module Def exists
    module_name = "Bizaxl Finance"
    if not frappe.db.exists("Module Def", module_name):
        try:
            module = frappe.get_doc({
                "doctype": "Module Def",
                "module_name": module_name,
                "app_name": "bizaxl_finance",
                "custom": 1
            })
            module.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"✅ Created Module Def: {module_name}")
        except Exception as e:
            frappe.db.rollback()
            print(f"❌ Failed to create Module Def: {str(e)}")
    else:
        print(f"⏭️ Module Def '{module_name}' already exists")

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

    # Step 2: Create single record (get_single auto-creates if missing)
    try:
        frappe.flags.in_import = True
        settings = frappe.get_single(doctype_name)
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.flags.in_import = False
        print(f"✅ Single record for '{doctype_name}' is ready")
    except Exception as e:
        frappe.db.rollback()
        frappe.flags.in_import = False
        print(f"❌ Failed to create single record: {str(e)}")

    print("=" * 60)
    print("Done! Integration Settings should now be accessible.")
    print("=" * 60)


fix()
