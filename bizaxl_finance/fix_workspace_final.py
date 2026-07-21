"""
Bizaxl Finance — FINAL Workspace Fix
=====================================
Uses direct database operations to force-update the workspace.
Auto-discovers table columns so it works on ANY Frappe version.

Usage:
    bench --site your-site console
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
    print("📦 BIZAXL FINANCE — FINAL WORKSPACE FIX")
    print("=" * 60)

    # ── Read fixture ───────────────────────────────────────────────────────
    base = frappe.get_app_path("bizaxl_finance")
    fixture_path = os.path.join(base, "workspace", "bizaxl_finance", "bizaxl_finance.json")

    if not os.path.exists(fixture_path):
        print(f"❌ Fixture not found: {fixture_path}")
        return

    with open(fixture_path) as f:
        fixture = json.load(f)

    content = fixture.get("content", "[]")
    all_links = fixture.get("links", [])

    cards = len(json.loads(content))
    print(f"\n📋 Fixture: {cards} cards, {len(all_links)} links, 0 shortcuts")

    # ── Step 1: DELETE old workspace ───────────────────────────────────────
    print("\n🔧 Step 1/3: Deleting old workspace...")
    if frappe.db.exists("Workspace", "Bizaxl Finance"):
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", "Bizaxl Finance")
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s AND parenttype = 'Workspace'", "Bizaxl Finance")
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", "Bizaxl Finance")
        frappe.db.commit()
        print("  ✅ Old workspace deleted")
    else:
        print("  ⏭️ No old workspace to delete")

    # ── Step 2: Discover columns & create workspace ────────────────────────
    print("\n🔧 Step 2/3: Discovering columns and creating workspace...")

    # Get actual columns from the table
    columns = [row[0] for row in frappe.db.sql("DESCRIBE `tabWorkspace`")]
    print(f"  Found columns: {', '.join(columns[:10])}... ({len(columns)} total)")

    now = frappe.utils.now()

    # Build column-value pairs dynamically based on what exists
    col_map = {
        "name": "Bizaxl Finance",
        "owner": "Administrator",
        "creation": now,
        "modified": now,
        "modified_by": "Administrator",
        "docstatus": 0,
        "idx": 0,
        "title": "Bizaxl Finance",
        "module": "Bizaxl Finance",
        "icon": "credit-card",
        "label": "Bizaxl Finance",
        "content": content,
    }

    # Add optional columns only if they exist
    optional_fields = {
        "is_default": 1,
        "public": 1,
        "sequence_id": 1.0,
        "is_hidden": 0,
        "is_standard": 0,
    }
    for field, value in optional_fields.items():
        if field in columns:
            col_map[field] = value

    # Build and execute INSERT
    col_names = list(col_map.keys())
    placeholders = ["%s"] * len(col_names)
    values = [col_map[c] for c in col_names]

    quoted = [f"`{c}`" for c in col_names]
    sql = f"INSERT INTO `tabWorkspace` ({', '.join(quoted)}) VALUES ({', '.join(placeholders)})"

    frappe.db.sql(sql, values)
    frappe.db.commit()
    print(f"  ✅ Workspace created with {len(col_names)} columns")

    # ── Step 3: Insert links in chunks ─────────────────────────────────────
    print(f"\n🔧 Step 3/3: Inserting {len(all_links)} links...")

    link_cols = ["parent", "parenttype", "parentfield", "idx",
                 "type", "label", "link_to", "link_type",
                 "hidden", "is_query_report", "onboard", "dependencies"]

    link_values = []
    for i, link in enumerate(all_links):
        link_values.append((
            "Bizaxl Finance",        # parent
            "Workspace",             # parenttype
            "links",                 # parentfield
            i,                       # idx
            link.get("type", ""),
            link.get("label", ""),
            link.get("link_to", ""),
            link.get("link_type", ""),
            link.get("hidden", 0),
            link.get("is_query_report", 0),
            link.get("onboard", 0),
            link.get("dependencies", ""),
        ))

    # Insert in chunks of 50
    chunk_size = 50
    for chunk_start in range(0, len(link_values), chunk_size):
        chunk = link_values[chunk_start:chunk_start + chunk_size]
        quoted = [f"`{c}`" for c in link_cols]
        ph = ",".join(["(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"] * len(chunk))
        frappe.db.sql(
            f"INSERT INTO `tabWorkspace Link` ({', '.join(quoted)}) VALUES {ph}",
            [val for row in chunk for val in row]
        )
        frappe.db.commit()
        print(f"    Inserted links {chunk_start+1}-{chunk_start+len(chunk)}")

    print(f"  ✅ {len(all_links)} links inserted")

    # ── Verify ─────────────────────────────────────────────────────────────
    print("\n🔧 Verifying...")
    ws = frappe.get_doc("Workspace", "Bizaxl Finance")
    final_cards = len(json.loads(ws.content))
    final_links = len(ws.links)
    final_shortcuts = len(ws.shortcuts)

    print(f"\n✅ WORKSPACE CREATED SUCCESSFULLY!")
    print(f"   Cards: {final_cards}")
    print(f"   Links: {final_links}")
    print(f"   Shortcuts: {final_shortcuts}")

    if final_cards >= 24:
        print("✅ All 24+ cards are present!")
    if final_links >= 100:
        print(f"✅ All {final_links} links present!")

    print("\n📋 Next steps:")
    print("   1. Exit console (Ctrl+D)")
    print("   2. bench --site your-site clear-cache")
    print("   3. bench restart")
    print("   4. Refresh browser (F5)")


fix_workspace_final()
