"""
Bizaxl Finance — Fix Workspace
===============================
Restores the Bizaxl Finance workspace from fixture JSON
with all 24 cards, 100+ links, and 13 shortcuts.

Usage:
    bench --site your-site console
    exec(open("../apps/bizaxl_finance/bizaxl_finance/fix_workspace.py").read())
    exit
    bench --site your-site clear-cache
"""

import frappe
import json
import os


def fix_workspace():
    print("=" * 60)
    print("📦 BIZAXL FINANCE — FIX WORKSPACE")
    print("=" * 60)

    # Read fixture
    base = frappe.get_app_path("bizaxl_finance")
    fixture_path = os.path.join(base, "workspace", "bizaxl_finance", "bizaxl_finance.json")

    if not os.path.exists(fixture_path):
        print(f"❌ Fixture not found: {fixture_path}")
        return

    with open(fixture_path) as f:
        fixture = json.load(f)

    print(f"\n📋 Fixture loaded: {len(json.loads(fixture['content']))} cards, {len(fixture['links'])} links, {len(fixture['shortcuts'])} shortcuts")

    # Get existing workspace or create new
    if frappe.db.exists("Workspace", "Bizaxl Finance"):
        ws = frappe.get_doc("Workspace", "Bizaxl Finance")
        print("📂 Existing workspace found, updating...")
    else:
        ws = frappe.get_doc({"doctype": "Workspace", "name": "Bizaxl Finance"})
        print("📂 Creating new workspace...")

    # Set core fields
    ws.label = "Bizaxl Finance"
    ws.module = "Bizaxl Finance"
    ws.title = "Bizaxl Finance"
    ws.icon = "credit-card"
    ws.is_hidden = 0
    ws.is_standard = 1
    ws.is_default = 1
    ws.public = 1
    ws.sequence_id = 1.0

    # Set content (cards JSON)
    ws.content = fixture["content"]

    # Replace links
    ws.set("links", [])
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

    # Replace shortcuts
    ws.set("shortcuts", [])
    for shortcut in fixture.get("shortcuts", []):
        ws.append("shortcuts", {
            "type": shortcut.get("type", "DocType"),
            "label": shortcut.get("label", ""),
            "link_to": shortcut.get("link_to", ""),
            "doc_view": shortcut.get("doc_view", "List"),
            "hidden": shortcut.get("hidden", 0),
        })

    # Bypass link validation for DocTypes that may not exist yet
    ws.flags.ignore_links = True
    ws.save(ignore_permissions=True)
    frappe.db.commit()

    # Verify
    cards = len(json.loads(ws.content))
    links = len(ws.links)
    shortcuts = len(ws.shortcuts)
    print(f"\n✅ WORKSPACE UPDATED SUCCESSFULLY!")
    print(f"   Cards: {cards}")
    print(f"   Links: {links}")
    print(f"   Shortcuts: {shortcuts}")

    if cards >= 24:
        print("✅ All 24+ cards are present!")
    if links >= 100:
        print(f"✅ All {links} links are present!")
    else:
        print(f"⚠️  {links} links (expected 100+)")

    print("\n📋 Next steps:")
    print("   1. Exit console (Ctrl+D)")
    print("   2. Run: bench --site your-site clear-cache")
    print("   3. Ctrl+Shift+R hard refresh in browser")

    return ws


# For exec() in Frappe console (__name__ != __main__ there)
# Also covers bench execute (import triggers this, then bench calls function again)
# Idempotent - running twice just re-saves the same data
fix_workspace()
