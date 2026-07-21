"""
Auto-syncs the Bizaxl Finance workspace from its fixture file after every migration.
This ensures the workspace always shows all 24 card sections regardless of
Frappe's sync behavior.

Called by the after_migrate hook in hooks.py
"""

import frappe
import json
import os


def sync_workspace_from_fixture():
    """Read the workspace fixture file and update the database record"""
    fixture_path = frappe.get_app_path(
        "bizaxl_finance", "workspace", "bizaxl_finance", "bizaxl_finance.json"
    )

    if not os.path.exists(fixture_path):
        frappe.log_error(
            f"Workspace fixture not found at {fixture_path}",
            "Workspace Sync"
        )
        return

    try:
        with open(fixture_path) as f:
            fixture = json.load(f)

        if not frappe.db.exists("Workspace", "Bizaxl Finance"):
            frappe.log_error("Workspace 'Bizaxl Finance' not found in database", "Workspace Sync")
            return

        ws = frappe.get_doc("Workspace", "Bizaxl Finance")
        ws.content = fixture.get("content", ws.content)

        # Rebuild links from fixture
        ws.set("links", [])
        for link in fixture.get("links", []):
            ws.append("links", {
                "type": link.get("type"),
                "label": link.get("label"),
                "link_to": link.get("link_to", ""),
                "link_type": link.get("link_type", ""),
                "hidden": link.get("hidden", 0),
                "is_query_report": link.get("is_query_report", 0),
                "onboard": link.get("onboard", 0),
            })

        # Rebuild shortcuts from fixture
        ws.set("shortcuts", [])
        for shortcut in fixture.get("shortcuts", []):
            ws.append("shortcuts", {
                "type": shortcut.get("type", "DocType"),
                "label": shortcut.get("label", ""),
                "link_to": shortcut.get("link_to", ""),
                "doc_view": shortcut.get("doc_view", "List"),
                "hidden": shortcut.get("hidden", 0),
            })

        # Bypass link validation (DocTypes may not exist yet during first migration)
        ws.flags.ignore_links = True

        # Disable developer_mode temporarily to prevent Workspace.on_update()
        # from trying to export to files (custom modules need a 'package' field)
        original_dev_mode = frappe.conf.developer_mode
        frappe.conf.developer_mode = 0

        ws.save(ignore_permissions=True)

        frappe.conf.developer_mode = original_dev_mode
        frappe.db.commit()

        cards = len(json.loads(ws.content))
        links = len(ws.links)
        shortcuts = len(ws.shortcuts)
        print(f"  ✅ Workspace synced: {cards} cards, {links} links, {shortcuts} shortcuts")

    except Exception as e:
        frappe.log_error(f"Workspace sync failed: {e}", "Workspace Sync")
        print(f"  ⚠️ Workspace sync failed: {e}")
