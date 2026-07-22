"""
Bizaxl Finance — Compare & Install Missing DocTypes
====================================================
Run this on your server to:
  1. Compare all doctypes in GitHub code vs your database
  2. Show which are missing
  3. Create the missing ones

Usage:
    bench --site finance.bizaxl.local execute bizaxl_finance.fix_doctypes.compare_and_install
"""

import frappe
import json
import os
import sys


def discover_doctype_paths(base_dir):
    """Walk the app directory and discover all doctype JSON files."""
    doctypes = []
    for root, dirs, files in os.walk(base_dir):
        if "doctype" not in root.split(os.sep):
            continue
        for f in files:
            if f.endswith(".json") and f != "property_setters.json":
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir)
                try:
                    with open(full_path) as fp:
                        data = json.load(fp)
                    if data.get("doctype") == "DocType" and data.get("name"):
                        doctypes.append((data["name"], rel_path, data.get("module", "")))
                except (json.JSONDecodeError, IOError):
                    pass

    # Sort by module then name
    def sort_key(item):
        name, rel_path, module = item
        return (module or "", name.lower())

    doctypes.sort(key=sort_key)
    return doctypes


def compare_and_install():
    """Main function — compare codebase doctypes with DB and install missing ones."""
    print("=" * 72)
    print("  Bizaxl Finance — Compare & Install Missing DocTypes")
    print("=" * 72)

    base_dir = frappe.get_app_path("bizaxl_finance")
    doctype_list = discover_doctype_paths(base_dir)
    total_in_code = len(doctype_list)

    print(f"\n  📂 Found {total_in_code} DocTypes in GitHub code\n")

    # Compare with database
    existing = []
    missing = []
    for doctype_name, rel_path, module in doctype_list:
        if frappe.db.exists("DocType", doctype_name):
            existing.append((doctype_name, module))
        else:
            missing.append((doctype_name, module, rel_path))

    # Print comparison
    print(f"  ✅ Already in database: {len(existing)}")
    print(f"  ❌ Missing from database: {len(missing)}")
    print(f"  ────────────────────────────")
    print(f"  Total in code: {total_in_code}")
    print()

    if missing:
        print("  ❌ MISSING DOCTYPES (will install):")
        print("-" * 72)
        # Group by module
        by_module = {}
        for name, module, path in missing:
            by_module.setdefault(module or "Uncategorized", []).append(name)
        for module, names in sorted(by_module.items()):
            print(f"\n  📁 {module}:")
            for n in names:
                print(f"     • {n}")
        print()
    else:
        print("  ✅ All doctypes from GitHub are already installed!")
        print()

    # Install missing ones
    if not missing:
        print("  ✅ Nothing to install. All done!")
        return {"status": "ok", "message": "All doctypes already installed"}

    print("=" * 72)
    print("  INSTALLING MISSING DOCTYPES...")
    print("=" * 72)

    created = []
    skipped = []
    failed = []

    for doctype_name, module, rel_path in missing:
        full_path = os.path.join(base_dir, rel_path)

        if not os.path.exists(full_path):
            print(f"  ⚠️  FILE NOT FOUND: {doctype_name}")
            continue

        with open(full_path) as f:
            data = json.load(f)

        try:
            # For singletons, don't use naming series
            if data.get("issingle"):
                data.pop("autoname", None)
                data.pop("naming_rule", None)
            
            doc = frappe.get_doc(data)
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"  ✅ CREATED: {doctype_name} [{module}]")
            created.append(doctype_name)
        except Exception as e:
            frappe.db.rollback()
            print(f"  ❌ FAILED: {doctype_name} — {str(e)}")
            failed.append(doctype_name)

    # Summary
    print()
    print("=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    print(f"  ✅ Created:  {len(created)}")
    print(f"  ❌ Failed:   {len(failed)}")
    print(f"  ─────────────────────")
    print(f"  Total installed: {len(created)}")
    print("=" * 72)

    if created:
        print(f"\n  ✅ Created: {', '.join(created)}")
    if failed:
        print(f"\n  ❌ Failed: {', '.join(failed)}")

    # Clear cache
    frappe.clear_cache()
    frappe.cache().delete_key("bootinfo")

    print("\n  ✅ All done! Refresh your workspace at /app/bizaxl-finance\n")

    return {
        "status": "ok" if not failed else "partial",
        "created": created,
        "created_count": len(created),
        "failed": failed,
        "failed_count": len(failed),
    }
