"""
Bizaxl Finance — Workspace Sync
================================
Fixed: Uses SQL to bypass link validation, only adds valid links.
"""

import frappe
import json
import os


def sync_workspace_from_fixture():
    """Recreate the Bizaxl Finance workspace using SQL (bypasses link validation)"""
    fixture_path = frappe.get_app_path(
        "bizaxl_finance", "workspace", "bizaxl_finance", "bizaxl_finance.json"
    )

    if not os.path.exists(fixture_path):
        print(f"  ❌ Workspace fixture not found")
        return

    try:
        with open(fixture_path) as f:
            fixture = json.load(f)

        content = fixture.get("content", "[]")
        all_links = fixture.get("links", [])

        cards_count = len(json.loads(content))
        print(f"  📋 Fixture has {cards_count} cards, {len(all_links)} links")

        # Get existing DocTypes and Reports
        existing_doctypes = set(frappe.db.get_all('DocType', pluck='name'))
        existing_reports = set(frappe.db.get_all('Report', pluck='name'))
        
        # Filter valid links only
        valid_links = []
        for link in all_links:
            link_to = link.get('link_to', '')
            link_type = link.get('link_type', '')
            
            if link_type == 'Card Break' or not link_to:
                valid_links.append(link)
            elif link_type == 'DocType' and link_to in existing_doctypes:
                valid_links.append(link)
            elif link_type == 'Report' and link_to in existing_reports:
                valid_links.append(link)
        
        print(f"  ✅ {len(valid_links)} valid links (filtered {len(all_links) - len(valid_links)} invalid)")

        # Delete existing workspace
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = 'Bizaxl Finance'")
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = 'Bizaxl Finance'")
        frappe.db.commit()

        # Create workspace via SQL (bypasses ORM validation)
        frappe.db.sql("""
            INSERT INTO `tabWorkspace` (
                name, title, label, module, icon, is_default, is_standard,
                is_hidden, public, sequence_id, owner, creation, modified, content
            ) VALUES (
                'Bizaxl Finance', 'Bizaxl Finance', 'Bizaxl Finance',
                'Bizaxl Finance', 'credit-card', 1, 0, 0, 1, 1.0, 'Administrator',
                NOW(), NOW(), %s
            )
        """, (content,))

        # Add valid links via SQL
        for idx, link in enumerate(valid_links):
            frappe.db.sql("""
                INSERT INTO `tabWorkspace Link` (
                    name, doctype, parent, parentfield, parenttype,
                    type, label, link_to, link_type, hidden, is_query_report, onboard
                ) VALUES (
                    %s, 'Workspace Link', 'Bizaxl Finance', 'links', 'Workspace',
                    %s, %s, %s, %s, 0, %s, %s
                )
            """, (
                f"ws_link_{idx}",
                link.get('type', ''),
                link.get('label', ''),
                link.get('link_to', ''),
                link.get('link_type', ''),
                link.get('is_query_report', 0),
                link.get('onboard', 0)
            ))

        frappe.db.commit()
        frappe.cache().delete_key("bootinfo")

        print(f"  ✅ Workspace created with {cards_count} cards and {len(valid_links)} links")

    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
