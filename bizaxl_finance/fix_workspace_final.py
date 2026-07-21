"""
Bizaxl Finance — SIMPLEST Workspace Fix
========================================
Uses the ORM end-to-end (no direct SQL) with all bypass flags.
Works because migrate_workspace.py (after_migrate hook) now also
has the same bypass flags, so migration won't break it.

Usage: bench --site your-site console
    exec(open("../apps/bizaxl_finance/bizaxl_finance/fix_workspace_final.py").read())
    exit
    bench --site your-site clear-cache
    bench restart
"""

import frappe
import json
import os


def fix_workspace_final():
    print("=" * 60)
    print("📦 BIZAXL FINANCE — SIMPLEST WORKSPACE FIX")
    print("=" * 60)

    # Read fixture
    base = frappe.get_app_path("bizaxl_finance")
    fixture_path = os.path.join(base, "workspace", "bizaxl_finance", "bizaxl_finance.json")
    if not os.path.exists(fixture_path):
        print(f"❌ Fixture not found: {fixture_path}")
        return

    with open(fixture_path) as f:
        fixture = json.load(f)

    print(f"\n📋 Fixture: {len(json.loads(fixture['content']))} cards, {len(fixture['links'])} links, {len(fixture.get('shortcuts',[]))} shortcuts")

    # Delete old workspace using ORM
    print("\n🔧 Step 1/3: Deleting old workspace...")
    if frappe.db.exists("Workspace", "Bizaxl Finance"):
        frappe.get_doc("Workspace", "Bizaxl Finance").delete()
        frappe.db.commit()
        print("  ✅ Old workspace deleted")
    else:
        print("  ⏭️ No old workspace to delete")

    # Create new workspace using ORM
    print("\n🔧 Step 2/3: Creating new workspace via ORM...")
    
    doc_data = {
        "doctype": "Workspace",
        "name": "Bizaxl Finance",
        "title": "Bizaxl Finance",
        "module": "Bizaxl Finance",
        "label": "Bizaxl Finance",
        "icon": "credit-card",
        "is_hidden": 0,
        "is_standard": 0,
        "is_default": 1,
        "public": 1,
        "sequence_id": 1.0,
        "content": fixture["content"],
    }
    
    ws = frappe.get_doc(doc_data)
    
    # Add links
    for link in fixture.get("links", []):
        ws.append("links", {
            "type": link.get("type", ""),
            "label": link.get("label", ""),
            "link_to": link.get("link_to", ""),
            "link_type": link.get("link_type", ""),
            "hidden": link.get("hidden", 0),
            "is_query_report": link.get("is_query_report", 0),
            "onboard": link.get("onboard", 0),
            "dependencies": link.get("dependencies", ""),
        })

    # Save with all bypass flags
    ws.flags.ignore_links = True
    original_dev_mode = frappe.conf.developer_mode
    try:
        frappe.conf.developer_mode = 0
        ws.insert(ignore_permissions=True, ignore_if_duplicate=True)
    finally:
        frappe.conf.developer_mode = original_dev_mode
    
    frappe.db.commit()
    print("  ✅ Workspace created via ORM")

    # Verify
    print("\n🔧 Step 3/3: Verifying...")
    ws = frappe.get_doc("Workspace", "Bizaxl Finance")
    cards = len(json.loads(ws.content))
    links = len(ws.links)
    shortcuts = len(ws.shortcuts)

    print(f"\n✅ WORKSPACE CREATED SUCCESSFULLY!")
    print(f"   Cards: {cards}")
    print(f"   Links: {links}")
    print(f"   Shortcuts: {shortcuts}")

    if cards >= 24:
        print("✅ All 24+ cards are present!")
    if links >= 100:
        print(f"✅ All {links} links present!")

    print("\n📋 Next steps:")
    print("   1. Exit console (Ctrl+D)")
    print("   2. bench --site your-site clear-cache")
    print("   3. bench restart")
    print("   4. Open INCOGNITO browser window")
    print("   5. Login and check Bizaxl Finance workspace")


fix_workspace_final()
