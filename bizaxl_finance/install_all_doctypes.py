"""
Install ALL DocTypes from the bizaxl_finance app into your Frappe site.

This script auto-discovers every doctype JSON file under the app's directory
tree and creates any that don't already exist in the database.

Usage:
    bench --site finance.bizaxl.org console
    exec(open("../apps/bizaxl_finance/bizaxl_finance/install_all_doctypes.py").read())
    exit
"""

import sys
import frappe
import json
import os


def discover_doctype_paths(base_dir):
    """
    Walk the app directory tree and discover all doctype JSON files.
    Returns a list of (doctype_name, relative_path) tuples sorted by directory
    to maintain a logical creation order (foundation first, then dependents).
    """
    doctypes = []

    # Priority ordering for modules (foundation/core modules first)
    priority_modules = [
        "foundation",
        "customer_management",
        "loans",
        "banking",
        "payments",
        "investments",
        "insurance",
        "credit_management",
        "portfolio_management",
    ]

    # Walk the entire app directory looking for doctype JSON files
    for root, dirs, files in os.walk(base_dir):
        if "doctype" not in root.split(os.sep):
            continue
        for f in files:
            if f.endswith(".json") and f != "property_setters.json":
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir)
                # Read the JSON to get the doctype name
                try:
                    with open(full_path) as fp:
                        data = json.load(fp)
                    if data.get("doctype") == "DocType" and data.get("name"):
                        doctypes.append((data["name"], rel_path, root))
                except (json.JSONDecodeError, IOError):
                    pass

    # Sort: priority modules first, then alphabetical
    def sort_key(item):
        name, rel_path, root = item
        # Extract module name from path (e.g., "foundation/doctype/...")
        parts = rel_path.replace("\\", "/").split("/")
        module = parts[0] if parts else ""
        priority = priority_modules.index(module) if module in priority_modules else 999
        return (priority, name.lower())

    doctypes.sort(key=sort_key)
    return [(name, rel_path) for name, rel_path, _ in doctypes]


def create_single_doctype(base_dir, doctype_name, relative_path):
    """Read a DocType JSON file and create it in the database."""
    full_path = os.path.join(base_dir, relative_path)

    if not os.path.exists(full_path):
        return f"⚠️  FILE NOT FOUND: {doctype_name} ({full_path})"

    with open(full_path) as f:
        data = json.load(f)

    # Check if already exists
    if frappe.db.exists("DocType", doctype_name):
        return f"⏭️  SKIP (exists): {doctype_name}"

    try:
        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return f"✅ CREATED: {doctype_name}"
    except Exception as e:
        frappe.db.rollback()
        return f"❌ FAILED: {doctype_name} — {str(e)}"


def install_on_app_install():
    """Called by after_install hook — installs all DocTypes on fresh app install."""
    base_dir = frappe.get_app_path("bizaxl_finance")
    doctype_list = discover_doctype_paths(base_dir)
    results = []
    for doctype_name, rel_path in doctype_list:
        result = create_single_doctype(base_dir, doctype_name, rel_path)
        results.append(result)
    ok = [r for r in results if r.startswith("✅")]
    fail = [r for r in results if r.startswith("❌")]
    print(f"[bizaxl_finance] after_install: created {len(ok)} doctypes, {len(fail)} failed")
    if fail:
        raise Exception(f"Failed to create {len(fail)} doctypes: {fail}")


def run():
    base_dir = frappe.get_app_path("bizaxl_finance")

    print("=" * 72)
    print("  Bizaxl Finance — Install All DocTypes")
    print("=" * 72)

    # Discover all doctypes
    doctype_list = discover_doctype_paths(base_dir)
    print(f"\n  Found {len(doctype_list)} DocType JSON files in app tree.\n")

    # Create each one
    results = []
    total = len(doctype_list)
    for i, (doctype_name, rel_path) in enumerate(doctype_list, 1):
        result = create_single_doctype(base_dir, doctype_name, rel_path)
        results.append(result)
        # Print progress
        status_icon = result[:2]
        print(f"  [{i}/{total}] {result}")
        # Flush output so it's visible in the console
        sys.stdout.flush()

    # Summary
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    ok = [r for r in results if r.startswith("✅")]
    skip = [r for r in results if r.startswith("⏭️")]
    fail = [r for r in results if r.startswith("❌")]
    nf = [r for r in results if r.startswith("⚠️")]
    print(f"  ✅ Created:      {len(ok)}")
    print(f"  ⏭️  Already existed: {len(skip)}")
    print(f"  ❌ Failed:       {len(fail)}")
    print(f"  ⚠️  Not found:    {len(nf)}")
    print(f"  ─────────────────────")
    print(f"  Total:           {total}")
    print("=" * 72)

    if fail:
        print("\n  ❌ Failed DocTypes:")
        for r in fail:
            print(f"     {r}")
    if nf:
        print("\n  ⚠️  Missing files:")
        for r in nf:
            print(f"     {r}")

    print("\n  ✅ Done! Run `bench migrate` next to apply any remaining patches.\n")


run()
