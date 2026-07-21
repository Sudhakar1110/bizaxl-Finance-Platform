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

        # ── Step 0: Ensure 'Bizaxl Finance' Module Def has a package ──
        # Frappe v15 requires custom modules to have a package set.
        # Without it, the workspace page API might fail with 400 errors.
        package_name = "Bizaxl"
        module_name = "Bizaxl Finance"
        
        if not frappe.db.exists("Package", package_name):
            package = frappe.get_doc({
                "doctype": "Package",
                "name": package_name,
                "package_name": package_name.lower(),
            })
            package.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"  ✅ Package '{package_name}' created")
        
        # Set package on the Module Def if not already set
        module_def = frappe.get_doc("Module Def", module_name)
        if not module_def.package:
            module_def.db_set("package", package_name)
            print(f"  ✅ Module '{module_name}' now has package '{package_name}'")
        
        # ── Step 1: Ensure the workspace row exists in tabWorkspace ──
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
            # Update content directly via SQL (module kept as 'Bizaxl Finance')
            frappe.db.sql("""
                UPDATE `tabWorkspace`
                SET `content` = %s,
                    `module` = 'Bizaxl Finance',
                    `label` = 'Bizaxl Finance',
                    `title` = 'Bizaxl Finance',
                    `modified` = NOW()
                WHERE `name` = %s
            """, (content, workspace_name))
            print(f"  ✅ Workspace content updated via SQL")

        # ── Step 2: Replace all links ──
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE `parent` = %s", workspace_name)
        
        # Discover actual columns in tabWorkspace Link
        link_cols = [r[0] for r in frappe.db.sql("DESCRIBE `tabWorkspace Link`")]
        
        for idx, link in enumerate(links):
            values = {}
            for col in link_cols:
                if col == "parent":
                    values[col] = workspace_name
                elif col == "parenttype":
                    values[col] = "Workspace"
                elif col == "parentfield":
                    values[col] = "links"
                elif col == "name":
                    # Generate unique name for child table - required in strict mode
                    values[col] = f"bizaxl-finance-link-{idx+1:05d}"
                elif col == "idx":
                    values[col] = idx + 1
                elif col in ("creation", "modified"):
                    values[col] = frappe.utils.now()
                elif col in ("owner", "modified_by"):
                    values[col] = "Administrator"
                elif col == "docstatus":
                    values[col] = 0
                elif col in ("hidden", "is_query_report", "onboard"):
                    values[col] = link.get(col, 0)
                elif col in ("_user_tags", "_comments", "_assign", "_liked_by"):
                    values[col] = ""
                else:
                    values[col] = link.get(col, "")
            
            cols_sql = ", ".join(f"`{c}`" for c in link_cols)
            placeholders = ", ".join(["%s"] * len(link_cols))
            vals_sql = tuple(values.get(c, "") for c in link_cols)
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace Link` ({cols_sql}) VALUES ({placeholders})",
                vals_sql
            )
        
        print(f"  ✅ {links_count} links synced")

        # ── Step 3: Replace all shortcuts ──
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE `parent` = %s", workspace_name)
        
        # Discover actual columns in tabWorkspace Shortcut
        sc_cols = [r[0] for r in frappe.db.sql("DESCRIBE `tabWorkspace Shortcut`")]
        
        for idx, shortcut in enumerate(shortcuts):
            values = {}
            for col in sc_cols:
                if col == "parent":
                    values[col] = workspace_name
                elif col == "parenttype":
                    values[col] = "Workspace"
                elif col == "parentfield":
                    values[col] = "shortcuts"
                elif col == "name":
                    # Generate unique name for child table - required in strict mode
                    values[col] = f"bizaxl-finance-shortcut-{idx+1:05d}"
                elif col == "idx":
                    values[col] = idx + 1
                elif col in ("creation", "modified"):
                    values[col] = frappe.utils.now()
                elif col in ("owner", "modified_by"):
                    values[col] = "Administrator"
                elif col == "docstatus":
                    values[col] = 0
                elif col == "hidden":
                    values[col] = shortcut.get(col, 0)
                elif col in ("_user_tags", "_comments", "_assign", "_liked_by"):
                    values[col] = ""
                else:
                    values[col] = shortcut.get(col, "")
            
            cols_sql = ", ".join(f"`{c}`" for c in sc_cols)
            placeholders = ", ".join(["%s"] * len(sc_cols))
            vals_sql = tuple(values.get(c, "") for c in sc_cols)
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace Shortcut` ({cols_sql}) VALUES ({placeholders})",
                vals_sql
            )
        
        frappe.db.commit()
        print(f"  ✅ {shortcuts_count} shortcuts synced")

        # ── Step 4: Clear workspace cache ──
        # Direct SQL bypasses Frappe's ORM cache, so we must invalidate it manually
        frappe.cache().delete_value(f"workspace:data:{workspace_name}")
        frappe.cache().hdel("workspace_data_keys", workspace_name)

        print(f"  ✅ BIZAXL FINANCE WORKSPACE: {cards_count} cards, {links_count} links, {shortcuts_count} shortcuts")

        # ── Step 5: ORM save to properly register workspace with Frappe ──
        # Direct SQL bypasses Frappe's registration mechanism. ORM save() 
        # ensures workspace is registered in Frappe's internal systems
        # so that get_workspace_sidebar_items() can find it.
        try:
            ws = frappe.get_doc("Workspace", workspace_name)
            ws.flags.ignore_links = True
            ws.content = content
            original_mode = frappe.conf.developer_mode
            try:
                frappe.conf.developer_mode = 0
                ws.save(ignore_permissions=True)
                print(f"  ✅ ORM save OK — workspace registered properly")
            finally:
                frappe.conf.developer_mode = original_mode
            frappe.db.commit()
            
            # Aggressive cache clearing
            frappe.cache().delete_value(f"workspace:data:{workspace_name}")
            frappe.cache().hdel("workspace_data_keys", workspace_name)
            frappe.cache().delete_keys("*workspace*")
            
            # Final verification
            ws_final = frappe.get_doc("Workspace", workspace_name)
            print(f"  ✅ Final: {len(json.loads(ws_final.content))} cards, {frappe.db.count('Workspace Link', {'parent': workspace_name})} links")
        except Exception as e:
            print(f"  ⚠️ ORM save optional: {e}")

    except Exception as e:
        frappe.log_error(f"Workspace sync failed: {str(e)}", "Workspace Sync")
        # Print full traceback for debugging
        import traceback
        print(f"  ❌ Workspace sync failed: {str(e)}")
        print(f"  Traceback: {traceback.format_exc()}")
