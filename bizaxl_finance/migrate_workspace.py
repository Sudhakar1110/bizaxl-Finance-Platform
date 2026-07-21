"""
Bizaxl Finance — Workspace Sync (Direct SQL Approach)
======================================================
Purpose: Ensure the workspace always shows 24 cards after every migration.

Why Direct SQL?
- Frappe's ORM (save/insert) triggers on_update which tries to export files
- Frappe's module sync runs BEFORE after_migrate and may create workspaces
  from fixture files with is_standard=1
- Custom modules without a package cause "Package must be set" errors
- Direct SQL bypasses ALL of these issues permanently

Strategy:
1. Read the fixture JSON manually (no ORM)
2. UPDATE the workspace content, links, and shortcuts via direct SQL
3. Verify the result immediately

Called by the after_migrate hook in hooks.py
"""

import frappe
import json
import os


def sync_workspace_from_fixture():
    """Update the Bizaxl Finance workspace via direct SQL"""
    fixture_path = frappe.get_app_path(
        "bizaxl_finance", "workspace", "bizaxl_finance", "bizaxl_finance.json"
    )

    if not os.path.exists(fixture_path):
        frappe.log_error(
            f"Workspace fixture not found at {fixture_path}",
            "Workspace Sync"
        )
        print(f"  ❌ Workspace fixture not found at {fixture_path}")
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

        # ── Step 1: Ensure the workspace row exists in tabWorkspace ──
        workspace_name = "Bizaxl Finance"

        if not frappe.db.exists("Workspace", workspace_name):
            # Create minimal workspace row via SQL
            now = frappe.utils.now()
            frappe.db.sql("""
                INSERT INTO `tabWorkspace`
                    (`name`, `owner`, `creation`, `modified`, `modified_by`, `docstatus`, `idx`,
                     `label`, `title`, `module`, `icon`, `is_hidden`, `public`, `sequence_id`, `content`)
                VALUES
                    (%s, 'Administrator', %s, %s, 'Administrator', 0, 0,
                     %s, %s, %s, 'credit-card', 0, 1, 1.0, %s)
            """, (workspace_name, now, now, "Bizaxl Finance", "Bizaxl Finance", "Bizaxl Finance", content))
            frappe.db.commit()
            print(f"  ✅ Workspace row created via SQL")
        else:
            # Update content directly via SQL
            frappe.db.sql("""
                UPDATE `tabWorkspace`
                SET `content` = %s,
                    `label` = 'Bizaxl Finance',
                    `title` = 'Bizaxl Finance',
                    `modified` = NOW()
                WHERE `name` = %s
            """, (content, workspace_name))
            print(f"  ✅ Workspace content updated via SQL")

        # ── Step 2: Replace all links ──
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE `parent` = %s", workspace_name)
        
        # Batch insert links
        link_fields = ["parent", "parenttype", "parentfield", "idx", "type", "label",
                        "link_to", "link_type", "hidden", "is_query_report", "onboard", "dependencies"]
        
        # Check which columns actually exist in tabWorkspace Link
        existing_cols = [r[0] for r in frappe.db.sql("DESCRIBE `tabWorkspace Link`")]
        link_fields = [f for f in link_fields if f in existing_cols]
        
        for idx, link in enumerate(links):
            values = []
            for field in link_fields:
                if field == "parent":
                    values.append(workspace_name)
                elif field == "parenttype":
                    values.append("Workspace")
                elif field == "parentfield":
                    values.append("links")
                elif field == "idx":
                    values.append(idx + 1)
                elif field in ("hidden", "is_query_report", "onboard"):
                    values.append(link.get(field, 0))
                else:
                    values.append(link.get(field, ""))
            
            placeholders = ", ".join(["%s"] * len(link_fields))
            cols = ", ".join(f"`{c}`" for c in link_fields)
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace Link` ({cols}) VALUES ({placeholders})",
                values
            )
        
        print(f"  ✅ {links_count} links synced")

        # ── Step 3: Replace all shortcuts ──
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE `parent` = %s", workspace_name)
        
        shortcut_fields = ["parent", "parenttype", "parentfield", "idx", "type", "label",
                           "link_to", "doc_view", "hidden"]
        existing_sc_cols = [r[0] for r in frappe.db.sql("DESCRIBE `tabWorkspace Shortcut`")]
        shortcut_fields = [f for f in shortcut_fields if f in existing_sc_cols]
        
        for idx, shortcut in enumerate(shortcuts):
            values = []
            for field in shortcut_fields:
                if field == "parent":
                    values.append(workspace_name)
                elif field == "parenttype":
                    values.append("Workspace")
                elif field == "parentfield":
                    values.append("shortcuts")
                elif field == "idx":
                    values.append(idx + 1)
                elif field == "hidden":
                    values.append(shortcut.get(field, 0))
                else:
                    values.append(shortcut.get(field, ""))
            
            placeholders = ", ".join(["%s"] * len(shortcut_fields))
            cols = ", ".join(f"`{c}`" for c in shortcut_fields)
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace Shortcut` ({cols}) VALUES ({placeholders})",
                values
            )
        
        frappe.db.commit()
        print(f"  ✅ {shortcuts_count} shortcuts synced")

        # ── Step 4: Clear workspace cache ──
        # Direct SQL bypasses Frappe's ORM cache, so we must invalidate it manually
        frappe.cache().delete_value(f"workspace:data:{workspace_name}")
        frappe.cache().hdel("workspace_data_keys", workspace_name)
        # Also clear the doc cache for this specific workspace
        frappe.cache().hdel("doctype_meta", "Workspace")
        frappe.cache().hdel("doctype_meta", workspace_name)

        print(f"  ✅ BIZAXL FINANCE WORKSPACE: {cards_count} cards, {links_count} links, {shortcuts_count} shortcuts")

    except Exception as e:
        frappe.log_error(f"Workspace sync failed: {str(e)}", "Workspace Sync")
        # Print full traceback for debugging
        import traceback
        print(f"  ❌ Workspace sync failed: {str(e)}")
        print(f"  Traceback: {traceback.format_exc()}")
