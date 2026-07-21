"""
Complete workspace fix - Delete and recreate with only valid links
Run in bench console:
bench --site finance.bizaxl.local console

Then paste this entire code:
"""

import frappe
import json

print("=" * 60)
print("COMPLETE WORKSPACE FIX")
print("=" * 60)

# Step 1: Get all existing DocTypes
print("\n1. Checking existing DocTypes...")
existing_doctypes = set(frappe.db.get_all('DocType', pluck='name'))
existing_reports = set(frappe.db.get_all('Report', pluck='name'))
print(f"   Found {len(existing_doctypes)} DocTypes, {len(existing_reports)} Reports")

# Step 2: Delete existing workspace
print("\n2. Deleting old workspace...")
if frappe.db.exists("Workspace", "Bizaxl Finance"):
    frappe.get_doc("Workspace", "Bizaxl Finance").delete()
    frappe.db.commit()
    print("   Deleted!")
else:
    print("   Not found, skipping...")

# Step 3: Read fixture
print("\n3. Reading fixture...")
fixture_path = frappe.get_app_path("bizaxl_finance", "fixtures", "workspace.json")
with open(fixture_path) as f:
    fixture = json.load(f)[0]

content = fixture.get("content", "[]")
links = fixture.get("links", [])
print(f"   Fixture: {len(json.loads(content))} cards, {len(links)} links")

# Step 4: Filter to only valid links
print("\n4. Filtering valid links...")
valid_links = []
invalid_links = []
for link in links:
    link_to = link.get('link_to', '')
    link_type = link.get('link_type', '')
    
    if link_type == 'Card Break' or not link_to:
        valid_links.append(link)
    elif link_type == 'DocType' and link_to:
        if link_to in existing_doctypes:
            valid_links.append(link)
        else:
            invalid_links.append(link_to)
    elif link_type == 'Report' and link_to:
        if link_to in existing_reports:
            valid_links.append(link)
        else:
            invalid_links.append(f"Report: {link_to}")
    else:
        valid_links.append(link)

print(f"   Valid links: {len(valid_links)}")
if invalid_links:
    print(f"   Invalid (removed): {len(invalid_links)}")
    for inv in invalid_links[:10]:
        print(f"      - {inv}")
    if len(invalid_links) > 10:
        print(f"      ... and {len(invalid_links) - 10} more")

# Step 5: Create new workspace
print("\n5. Creating new workspace...")
ws = frappe.get_doc({
    "doctype": "Workspace",
    "name": "Bizaxl Finance",
    "title": "Bizaxl Finance",
    "label": "Bizaxl Finance",
    "module": "Bizaxl Finance",
    "icon": "credit-card",
    "is_hidden": 0,
    "is_standard": 0,
    "public": 1,
    "sequence_id": 1.0,
    "content": content,
})

# Add valid links
for link in valid_links:
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

# Save with bypass
ws.flags.ignore_links = True
ws.flags.ignore_mandatory = True
ws.insert(ignore_permissions=True, ignore_if_duplicate=True)
frappe.db.commit()

# Step 6: Clear cache
print("\n6. Clearing cache...")
frappe.cache().delete_value("workspace:data:Bizaxl Finance")
frappe.cache().delete_key("bootinfo")

# Step 7: Verify
print("\n7. Verifying...")
ws2 = frappe.get_doc("Workspace", "Bizaxl Finance")
cards = json.loads(ws2.content)
print(f"   Cards: {len(cards)}")
print(f"   Links: {len(ws2.links)}")

print("\n" + "=" * 60)
print("DONE! Clear browser cache and refresh.")
print("=" * 60)
