"""Bizaxl Finance — Setup & Uninstall Hooks"""

import frappe


def before_uninstall():
    """Delete bizaxl_finance custom doctypes before modules are deleted.
    
    During uninstall-app, Frappe deletes modules before doctypes.
    This causes errors when doctypes reference modules already deleted.
    
    This hook pre-deletes the doctypes via direct SQL before Frappe
    starts the module deletion process.
    """
    # Get all doctypes belonging to bizaxl_finance modules
    bizaxl_modules = frappe.get_all("Module Def", 
        filters={"app_name": "bizaxl_finance"},
        pluck="module_name"
    )
    
    for module in bizaxl_modules:
        doctypes = frappe.get_all("DocType", 
            filters={"module": module},
            pluck="name"
        )
        for dt in doctypes:
            try:
                frappe.delete_doc("DocType", dt, ignore_on_trash=True, force=True)
                print(f"  Deleted DocType: {dt}")
            except Exception:
                # Fallback to direct SQL
                frappe.db.sql(f"DELETE FROM `tabDocType` WHERE `name` = %s", dt)
                frappe.db.sql(f"DROP TABLE IF EXISTS `tab{dt.replace(' ', '_')}`")
        
    frappe.db.commit()
    print(f"✅ Cleaned up {sum(1 for m in bizaxl_modules for _ in frappe.get_all('DocType', filters={'module': m}, pluck='name'))} doctypes")
