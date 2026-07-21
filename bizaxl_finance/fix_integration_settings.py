"""
Fix Integration Settings DocType and Module Def.

Root cause: 'Bizaxl Finance' Module Def exists in DB but is missing
'app_name' field. Frappe's get_module_app() can't find it, causing
'Module Bizaxl Finance not found' error during migration and save.

Fix:
1. Update 'Bizaxl Finance' Module Def with correct app_name
2. Create Integration Settings DocType definition (if missing)
3. Create Integration Settings single record (if missing)

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

    # Step 0: Fix 'Bizaxl Finance' Module Def - ensure app_name is set
    module_name = "Bizaxl Finance"
    if frappe.db.exists("Module Def", module_name):
        current_app = frappe.db.get_value("Module Def", module_name, "app_name")
        if current_app != "bizaxl_finance":
            frappe.db.set_value("Module Def", module_name, "app_name", "bizaxl_finance")
            frappe.db.set_value("Module Def", module_name, "custom", 1)
            frappe.db.commit()
            print(f"✅ Updated Module Def '{module_name}' with app_name='bizaxl_finance'")
        else:
            print(f"⏭️ Module Def '{module_name}' already has correct app_name")
    else:
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
