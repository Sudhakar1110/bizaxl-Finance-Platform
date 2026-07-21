"""
Bizaxl Finance — FINAL Workspace Fix
=====================================
Hybrid approach:
- Direct SQL (with DESCRIBE) to create workspace record
- ORM with ignore_links to add child table links
- Bypasses ALL Frappe hooks on the workspace save

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

    # ── Step 1: DELETE old workspace completely ────────────────────────────
    print("\n🔧 Step 1/4: Deleting old workspace...")
    exists = False
    if frappe.db.exists("Workspace", "Bizaxl Finance"):
        exists = True
        # Delete child records first
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", "Bizaxl Finance")
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s AND parenttype = 'Workspace'", "Bizaxl Finance")
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", "Bizaxl Finance")
        frappe.db.commit()
        print("  ✅ Old workspace deleted")
    else:
        print("  ⏭️ No old workspace to delete")

    # ── Step 2: Discover columns & create workspace via SQL ────────────────
    print("\n🔧 Step 2/4: Discovering columns and creating workspace...")

    columns = [row[0] for row in frappe.db.sql("DESCRIBE `tabWorkspace`")]
    print(f"  Found {len(columns)} columns in tabWorkspace")

    now = frappe.utils.now()

    # Build column-value pairs
    col_map = {}
    for col in columns:
        if col in ("name",):
            col_map[col] = "Bizaxl Finance"
        elif col in ("owner", "modified_by"):
            col_map[col] = "Administrator"
        elif col in ("creation", "modified"):
            col_map[col] = now
        elif col in ("docstatus", "idx"):
            col_map[col] = 0
        elif col in ("title", "module", "label"):
            col_map[col] = "Bizaxl Finance"
        elif col == "icon":
            col_map[col] = "credit-card"
        elif col == "content":
            col_map[col] = content
        elif col in ("is_default", "public"):
            col_map[col] = 1
        elif col in ("sequence_id",):
            col_map[col] = 1.0
        elif col in ("is_hidden", "is_standard"):
            col_map[col] = 0
        elif col in ("_user_tags", "_comments", "_assign", "_liked_by", "):
            col_map[col] = ""

    # Execute INSERT
    col_names = list(col_map.keys())
    placeholders = ["%s"] * len(col_names)
    values = [col_map[c] for c in col_names]
    quoted = [f"`{c}`" for c in col_names]

    sql = f"INSERT INTO `tabWorkspace` ({', '.join(quoted)}) VALUES ({', '.join(placeholders)})"
    frappe.db.sql(sql, values)
    frappe.db.commit()
    print(f"  ✅ Workspace created with {len(col_names)} columns")

    # ── Step 3: Add links via ORM (handles child table correctly) ──────────
    print(f"\n🔧 Step 3/4: Adding {len(all_links)} links via ORM...")

    ws = frappe.get_doc("Workspace", "Bizaxl Finance")
    ws.flags.ignore_links = True

    for link in all_links:
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

    original_dev_mode = frappe.conf.developer_mode
    try:
        frappe.conf.developer_mode = 0
        ws.save(ignore_permissions=True)
    finally:
        frappe.conf.developer_mode = original_dev_mode

    frappe.db.commit()
    print(f"  ✅ Links added via ORM")

    # ── Step 4: Verify ─────────────────────────────────────────────────────
    print("\n🔧 Step 4/4: Verifying...")
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

    return ws


fix_workspace_final()
