"""
Auto-syncs the Bizaxl Finance workspace from its fixture file after every migration.
This ensures the workspace always shows all 24 card sections regardless of
Frappe's sync behavior.

Called by the after_migrate hook in hooks.py

Uses pure ORM approach: deletes existing workspace, recreates from fixture
with all required metadata fields and bypass flags.
"""

import frappe
import json
import os


def sync_workspace_from_fixture():
    """Read the workspace fixture file and recreate the workspace in database"""
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

        cards_count = len(json.loads(fixture.get("content", "[]")))
        links_count = len(fixture.get("links", []))
        shortcuts_count = len(fixture.get("shortcuts", []))

        # ── Delete existing workspace if any ──
        if frappe.db.exists("Workspace", "Bizaxl Finance"):
            try:
                ws_old = frappe.get_doc("Workspace", "Bizaxl Finance")
                ws_old.delete()
                frappe.db.commit()
            except Exception:
                # If delete via ORM fails, force delete via SQL
                frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE `parent` = 'Bizaxl Finance'")
                frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE `parent` = 'Bizaxl Finance'")
                frappe.db.sql("DELETE FROM `tabWorkspace` WHERE `name` = 'Bizaxl Finance'")
                frappe.db.commit()

        # ── Create new workspace using pure ORM ──
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

        # Add shortcuts
        for shortcut in fixture.get("shortcuts", []):
            ws.append("shortcuts", {
                "type": shortcut.get("type", "DocType"),
                "label": shortcut.get("label", ""),
                "link_to": shortcut.get("link_to", ""),
                "doc_view": shortcut.get("doc_view", "List"),
                "hidden": shortcut.get("hidden", 0),
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

        print(f"  ✅ Workspace synced: {cards_count} cards, {links_count} links, {shortcuts_count} shortcuts")

    except Exception as e:
        frappe.log_error(f"Workspace sync failed: {str(e)}", "Workspace Sync")
        print(f"  ⚠️ Workspace sync failed: {str(e)}")
