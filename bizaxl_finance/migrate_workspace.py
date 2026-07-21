"""
Bizaxl Finance — Workspace Sync (Pure ORM Approach)
====================================================
Purpose: Ensure the workspace always shows 24 cards after every migration.

Why Pure ORM now?
- Previously ORM failed because Module 'Bizaxl Finance' had no Package
- Now we set Package='Bizaxl' on the Module Def before syncing the workspace
- ORM insert() ensures Frappe properly registers the workspace in ALL systems
- Direct SQL worked for DB updates but bypassed Frappe's registration mechanism

Strategy:
1. Read fixture JSON
2. Ensure Module Def has package set
3. DELETE existing workspace (if any)
4. INSERT new workspace via ORM with all bypass flags
5. Verify

Called by the after_migrate hook in hooks.py
"""

import frappe
import json
import os


def sync_workspace_from_fixture():
    """Recreate the Bizaxl Finance workspace via pure ORM"""
    fixture_path = frappe.get_app_path(
        "bizaxl_finance", "workspace", "bizaxl_finance", "bizaxl_finance.json"
    )

    if not os.path.exists(fixture_path):
        frappe.log_error(f"Workspace fixture not found at {fixture_path}", "Workspace Sync")
        print(f"  ❌ Workspace fixture not found")
        return

    try:
        with open(fixture_path) as f:
            fixture = json.load(f)

        content = fixture.get("content", "[]")
        links = fixture.get("links", [])
        shortcuts = fixture.get("shortcuts", [])

        cards_count = len(json.loads(content))
        links_count = len(links)
        shortcuts_count = len(shortcuts)

        print(f"  📋 Fixture has {cards_count} cards, {links_count} links, {shortcuts_count} shortcuts")

        workspace_name = "Bizaxl Finance"

        # ── Step 1: Ensure Module Def has a package ──
        if not frappe.db.exists("Package", "Bizaxl"):
            pkg = frappe.get_doc({
                "doctype": "Package",
                "name": "Bizaxl",
                "package_name": "bizaxl",
            })
            pkg.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"  ✅ Package 'Bizaxl' created")

        module_def = frappe.get_doc("Module Def", "Bizaxl Finance")
        if not module_def.package:
            module_def.db_set("package", "Bizaxl")
            print(f"  ✅ Module 'Bizaxl Finance' has package 'Bizaxl'")

        # ── Step 2: Delete existing workspace ──
        if frappe.db.exists("Workspace", workspace_name):
            frappe.get_doc("Workspace", workspace_name).delete()
            frappe.db.commit()
            print(f"  ✅ Old workspace deleted")

        # ── Step 3: Create workspace via pure ORM ──
        ws = frappe.get_doc({
            "doctype": "Workspace",
            "name": workspace_name,
            "title": "Bizaxl Finance",
            "label": "Bizaxl Finance",
            "module": "Bizaxl Finance",
            "icon": "credit-card",
            "is_hidden": 0,
            "is_standard": 0,
            "public": 1,
            "sequence_id": 1.0,
            "content": content,
        })

        # Add links
        for idx, link in enumerate(links):
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

        # Add shortcuts
        for idx, shortcut in enumerate(shortcuts):
            ws.append("shortcuts", {
                "type": shortcut.get("type", "DocType"),
                "label": shortcut.get("label", ""),
                "link_to": shortcut.get("link_to", ""),
                "doc_view": shortcut.get("doc_view", "List"),
                "hidden": shortcut.get("hidden", 0),
            })

        # Insert with all bypass flags
        ws.flags.ignore_links = True
        original_dev_mode = frappe.conf.developer_mode
        try:
            frappe.conf.developer_mode = 0
            ws.insert(ignore_permissions=True, ignore_if_duplicate=True)
        finally:
            frappe.conf.developer_mode = original_dev_mode

        frappe.db.commit()

        # ── Step 4: Clear cache ──
        frappe.cache().delete_value(f"workspace:data:{workspace_name}")
        frappe.cache().hdel("workspace_data_keys", workspace_name)

        # ── Step 5: Verify ──
        ws_final = frappe.get_doc("Workspace", workspace_name)
        final_cards = len(json.loads(ws_final.content))
        final_links = len(ws_final.links)

        print(f"  ✅ Workspace created via ORM: {final_cards} cards, {final_links} links")
        print(f"  ✅ Module: '{ws_final.module}', Public: {ws_final.public}")

    except Exception as e:
        frappe.log_error(f"Workspace sync failed: {str(e)}", "Workspace Sync")
        import traceback
        print(f"  ❌ Workspace sync failed: {str(e)}")
        print(f"     {traceback.format_exc()}")
