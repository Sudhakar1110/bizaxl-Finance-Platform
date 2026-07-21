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
        # Get actual columns from the table
        cols = [r[0] for r in frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`")]
        
        insert_cols = ["name", "title", "label", "module", "icon", "is_standard", "is_hidden", "public", "sequence_id", "owner", "creation", "modified", "content"]
        insert_cols = [c for c in insert_cols if c in cols]
        
        values = ["%s"] * len(insert_cols)
        placeholders = ", ".join(["`%s`"] * len(insert_cols)) % tuple(insert_cols)
        
        if "is_standard" not in cols:
            # Use different column names for older Frappe versions
            insert_cols = ["name", "title", "label", "module", "icon", "public", "sequence_id", "owner", "creation", "modified", "content"]
            insert_cols = [c for c in insert_cols if c in cols]
        
        placeholders = ", ".join(["`%s`"] * len(insert_cols)) % tuple(insert_cols)
        
        insert_sql = f"""
            INSERT INTO `tabWorkspace` ({placeholders}) VALUES ({", ".join(["%s"] * len(insert_cols))})
        """
        
        vals = []
        for c in insert_cols:
            if c == "name": vals.append("Bizaxl Finance")
            elif c == "title": vals.append("Bizaxl Finance")
            elif c == "label": vals.append("Bizaxl Finance")
            elif c == "module": vals.append("Bizaxl Finance")
            elif c == "icon": vals.append("credit-card")
            elif c == "public": vals.append(1)
            elif c == "sequence_id": vals.append(1.0)
            elif c == "owner": vals.append("Administrator")
            elif c == "creation": vals.append(frappe.utils.now())
            elif c == "modified": vals.append(frappe.utils.now())
            elif c == "content": vals.append(content)
            elif c == "is_standard": vals.append(0)
            elif c == "is_hidden": vals.append(0)
        
        frappe.db.sql(insert_sql, vals)

        # Add valid links via SQL - get actual columns
        link_cols = [r[0] for r in frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Link`")]
        link_insert_cols = ["name", "parent", "parentfield", "parenttype", "type", "label", "link_to", "link_type", "hidden", "is_query_report", "onboard"]
        link_insert_cols = [c for c in link_insert_cols if c in link_cols]
        
        for idx, link in enumerate(valid_links):
            vals = []
            for c in link_insert_cols:
                if c == "name": vals.append(f"ws_link_{idx}")
                elif c == "parent": vals.append("Bizaxl Finance")
                elif c == "parentfield": vals.append("links")
                elif c == "parenttype": vals.append("Workspace")
                elif c == "type": vals.append(link.get('type', ''))
                elif c == "label": vals.append(link.get('label', ''))
                elif c == "link_to": vals.append(link.get('link_to', ''))
                elif c == "link_type": vals.append(link.get('link_type', ''))
                elif c == "hidden": vals.append(0)
                elif c == "is_query_report": vals.append(link.get('is_query_report', 0))
                elif c == "onboard": vals.append(link.get('onboard', 0))
            
            cols_str = ", ".join([f"`{c}`" for c in link_insert_cols])
            vals_str = ", ".join(["%s"] * len(link_insert_cols))
            frappe.db.sql(f"INSERT INTO `tabWorkspace Link` ({cols_str}) VALUES ({vals_str})", vals)

        frappe.db.commit()
        frappe.cache().delete_key("bootinfo")

        print(f"  ✅ Workspace created with {cards_count} cards and {len(valid_links)} links")

    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
