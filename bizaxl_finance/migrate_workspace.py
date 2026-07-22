"""
Bizaxl Finance — Workspace Sync (ORM-based)
============================================
Uses the ORM end-to-end (no direct SQL) with all bypass flags.
This is called by the after_migrate hook in hooks.py.
"""

import frappe
import json
import os


def sync_workspace_from_fixture():
    """Recreate the Bizaxl Finance workspace using ORM with all bypass flags."""
    base = frappe.get_app_path("bizaxl_finance")
    fixture_path = os.path.join(base, "workspace", "bizaxl_finance", "bizaxl_finance.json")

    if not os.path.exists(fixture_path):
        print("  ❌ Workspace fixture not found")
        return

    with open(fixture_path) as f:
        fixture = json.load(f)

    print(f"  📋 Fixture: {len(json.loads(fixture['content']))} cards, {len(fixture['links'])} links")

    # Delete old workspace
    if frappe.db.exists("Workspace", "Bizaxl Finance"):
        frappe.get_doc("Workspace", "Bizaxl Finance").delete()
        frappe.db.commit()
        print("  ✅ Old workspace deleted")

    # Build new workspace doc from fixture
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

    # Add all links from fixture
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

    # Insert with ALL bypass flags to avoid link/module validation errors
    ws.flags.ignore_links = True
    original_dev_mode = frappe.conf.developer_mode
    try:
        frappe.conf.developer_mode = 0
        ws.insert(ignore_permissions=True, ignore_if_duplicate=True)
        frappe.db.commit()
    finally:
        frappe.conf.developer_mode = original_dev_mode

    # Clear cache so workspace appears immediately
    frappe.cache().delete_key("bootinfo")

    print(f"  ✅ Workspace created with {len(json.loads(ws.content))} cards and {len(ws.links)} links")
