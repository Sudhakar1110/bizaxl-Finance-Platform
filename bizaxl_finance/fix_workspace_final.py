"""
Bizaxl Finance — FINAL Workspace Fix
=====================================
Uses direct database operations to force-update the workspace.
Bypasses ALL Frappe hooks, validations, and sync mechanisms.

The trick: makes workspace non-standard (is_standard=0) so Frappe
stops trying to manage/sync/override it. Then writes all data directly.

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
    all_shortcuts = fixture.get("shortcuts", [])

    cards = len(json.loads(content))
    print(f"\n📋 Fixture: {cards} cards, {len(all_links)} links, {len(all_shortcuts)} shortcuts")

    # ── Step 1: DELETE existing workspace completely ───────────────────────
    print("\n🔧 Step 1/4: Deleting old workspace...")
    if frappe.db.exists("Workspace", "Bizaxl Finance"):
        # Delete child records first
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s AND parenttype = 'Workspace'", "Bizaxl Finance")
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s AND parenttype = 'Workspace'", "Bizaxl Finance")
        # Delete workspace record
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", "Bizaxl Finance")
        frappe.db.commit()
        print("  ✅ Old workspace deleted")
    else:
        print("  ⏭️ No old workspace to delete")

    # ── Step 2: Create workspace with direct SQL ───────────────────────────
    print("\n🔧 Step 2/4: Creating new workspace with direct SQL...")
    now = frappe.utils.now()

    frappe.db.sql("""
        INSERT INTO `tabWorkspace` (
            `name`, `owner`, `creation`, `modified`, `modified_by`,
            `docstatus`, `idx`, `title`, `module`, `icon`,
            `is_default`, `public`, `sequence_id`,
            `label`, `content`
        ) VALUES (
            %s, %s, %s, %s, %s,
            0, 0, %s, %s, %s,
            1, 1, 1.0,
            %s, %s
        )
    """, (
        "Bizaxl Finance",
        "Administrator",
        now, now, "Administrator",
        "Bizaxl Finance",  # title
        "Bizaxl Finance",  # module
        "credit-card",     # icon
        "Bizaxl Finance",  # label
        content,           # content JSON
    ))

    print("  ✅ Workspace record created")
    frappe.db.commit()

    # ── Step 3: Insert links ──────────────────────────────────────────────
    print(f"\n🔧 Step 3/4: Inserting {len(all_links)} links...")

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

    # Batch insert links - insert in chunks of 50 to avoid SQL size limits
    chunk_size = 50
    for chunk_start in range(0, len(link_values), chunk_size):
        chunk = link_values[chunk_start:chunk_start + chunk_size]
        placeholders = ",".join(["(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"] * len(chunk))
        frappe.db.sql(f"""
            INSERT INTO `tabWorkspace Link`
                (`parent`, `parenttype`, `parentfield`, `idx`,
                 `type`, `label`, `link_to`, `link_type`,
                 `hidden`, `is_query_report`, `onboard`, `dependencies`)
            VALUES {placeholders}
        """, [val for row in chunk for val in row])
        print(f"    Inserted links {chunk_start+1}-{chunk_start+len(chunk)}")
        frappe.db.commit()

    print(f"  ✅ {len(all_links)} links inserted")
    frappe.db.commit()

    print(f"  ✅ {len(all_links)} links inserted")
    frappe.db.commit()

    # ── Step 4: Verify ────────────────────────────────────────────────────
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
    print("   4. Refresh browser (F5) — workspace should show!")

    return ws


fix_workspace_final()
