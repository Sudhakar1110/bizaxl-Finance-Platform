"""
Bizaxl Finance — Compare & Install Missing DocTypes
====================================================
Run this on your server to:
  1. Compare all doctypes in GitHub code vs your database
  2. Show which are missing
  3. Create the missing ones
  4. Recreate the workspace (so it's no longer empty)

Usage:
    bench --site finance.bizaxl.local execute bizaxl_finance.fix_doctypes.compare_and_install
"""

import frappe
import json
import os
import sys

# Reuse the discovery logic from install_all_doctypes
from bizaxl_finance.install_all_doctypes import discover_doctype_paths


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
    for doctype_name, rel_path in doctype_list:
        if frappe.db.exists("DocType", doctype_name):
            existing.append(doctype_name)
        else:
            # Read module from the JSON file
            full_path = os.path.join(base_dir, rel_path)
            module = ""
            try:
                with open(full_path) as fp:
                    data = json.load(fp)
                    module = data.get("module", "")
            except Exception:
                pass
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
        print("  ✅ Nothing to install.")
        print("  🔧 Still recreating workspace to fix empty workspace issue...")
    else:
        print("=" * 72)
        print("  INSTALLING MISSING DOCTYPES...")
        print("=" * 72)

        created = []
        failed = []

        for doctype_name, module, rel_path in missing:
            full_path = os.path.join(base_dir, rel_path)

            if not os.path.exists(full_path):
                print(f"  ⚠️  FILE NOT FOUND: {doctype_name}")
                continue

            with open(full_path) as f:
                data = json.load(f)

            try:
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
        print("  INSTALL SUMMARY")
        print("=" * 72)
        print(f"  ✅ Created:  {len(created)}")
        print(f"  ❌ Failed:   {len(failed)}")
        print("=" * 72)

        if created:
            print(f"\n  ✅ Newly installed: {', '.join(created)}")
        if failed:
            print(f"\n  ❌ Failed: {', '.join(failed)}")

    # ── Recreate workspace ─────────────────────────────────────────────
    print()
    print("=" * 72)
    print("  RECREATING WORKSPACE...")
    print("=" * 72)
    
    from bizaxl_finance.migrate_workspace import sync_workspace_from_fixture
    sync_workspace_from_fixture()

    # Clear cache so everything appears immediately
    frappe.clear_cache()
    frappe.cache().delete_key("bootinfo")

    print()
    print("  ✅ Done! Everything should now appear at:")
    print("     http://finance.bizaxl.local/app/bizaxl-finance")
    print()
