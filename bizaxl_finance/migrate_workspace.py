"""
Auto-syncs the Bizaxl Finance workspace from its fixture file after every migration.
This ensures the workspace always shows all 24 card sections regardless of
Frappe's sync behavior.

Called by the after_migrate hook in hooks.py
"""

import frappe, json, os


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
            link_to = link.get("link_to", "")
            # Skip links to DocTypes that don't exist in the database
            if link.get("link_type") == "DocType" and link_to:
                if not frappe.db.exists("DocType", link_to):
                    continue
            ws.append("links", {
                "type": link.get("type"),
                "label": link.get("label"),
                "link_to": link_to,
                "link_type": link.get("link_type", ""),
                "hidden": link.get("hidden", 0),
                "is_query_report": link.get("is_query_report", 0),
                "onboard": link.get("onboard", 0),
            })

        ws.save(ignore_permissions=True)
        frappe.db.commit()

        cards = len(json.loads(ws.content))
        links = len(ws.links)
        print(f"  ✅ Workspace synced: {cards} cards, {links} links")

    except Exception as e:
        frappe.log_error(f"Workspace sync failed: {e}", "Workspace Sync")
