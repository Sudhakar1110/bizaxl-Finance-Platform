"""Bizaxl Finance — Setup & Uninstall Hooks"""

import frappe


def before_uninstall():
    """Delete bizaxl_finance custom doctypes before modules are deleted.
    
    During uninstall-app, Frappe deletes modules before doctypes.
    This causes errors when doctypes reference modules already deleted.
    
    This hook pre-deletes the doctypes via direct SQL before Frappe
    starts the module deletion process. Uses direct SQL only to avoid
    webhook circular dependency issues (e.g. deleting "Webhook" DocType).
    """
    bizaxl_modules = frappe.get_all("Module Def", 
        filters={"app_name": "bizaxl_finance"},
        pluck="module_name"
    )
    
    total = 0
    frappe.db.commit()  # Ensure clean transaction state
    
    for module in bizaxl_modules:
        doctypes = frappe.get_all("DocType", 
            filters={"module": module},
            pluck="name"
        )
        for dt in doctypes:
            table_name = f"tab{dt.replace(' ', '_')}"
            try:
                frappe.db.sql(f"DELETE FROM `tabDocType` WHERE `name` = %s", dt)
                frappe.db.sql(f"DROP TABLE IF EXISTS `{table_name}`")
                frappe.db.commit()
                print(f"  Deleted DocType: {dt}")
                total += 1
            except Exception as e:
                print(f"  ⚠️ Could not delete {dt}: {e}")
        
    print(f"✅ Cleaned up {total} doctypes")
