"""
Quick Workspace Restore - Run in bench console:
bench --site finance.bizaxl.local console
"""
import frappe
import json

print("Checking workspace...")

# Check if workspace exists
if frappe.db.exists("Workspace", "Bizaxl Finance"):
    ws = frappe.get_doc("Workspace", "Bizaxl Finance")
    cards = json.loads(ws.content) if ws.content else []
    print(f"Workspace exists: {len(cards)} cards, {len(ws.links)} links")
    if len(cards) == 0:
        print("Workspace is empty - will recreate...")
        ws.delete()
        frappe.db.commit()
        workspace_exists = False
    else:
        workspace_exists = True
else:
    print("Workspace not found - will create...")
    workspace_exists = False

if not workspace_exists:
    # Read fixture
    fixture_path = frappe.get_app_path("bizaxl_finance", "fixtures", "workspace.json")
    with open(fixture_path) as f:
        fix = json.load(f)[0]
    
    # Get existing DocTypes
    existing = set(frappe.db.get_all('DocType', pluck='name'))
    print(f"Existing DocTypes: {len(existing)}")
    
    # Filter valid links
    valid_links = []
    for l in fix['links']:
        link_to = l.get('link_to', '')
        link_type = l.get('link_type', '')
        if link_type == 'Card Break' or not link_to:
            valid_links.append(l)
        elif link_type == 'DocType' and link_to in existing:
            valid_links.append(l)
    
    print(f"Valid links: {len(valid_links)}")
    
    # Create workspace
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
        "content": fix['content']
    })
    
    for l in valid_links:
        ws.append("links", {
            "type": l.get("type"),
            "label": l.get("label"),
            "link_to": l.get("link_to"),
            "link_type": l.get("link_type"),
            "hidden": 0,
            "is_query_report": l.get("is_query_report", 0),
            "onboard": l.get("onboard", 0)
        })
    
    ws.flags.ignore_links = True
    ws.flags.ignore_mandatory = True
    ws.insert(ignore_permissions=True, ignore_if_duplicate=True)
    frappe.db.commit()
    
    print("Workspace recreated!")

# Final check
ws = frappe.get_doc("Workspace", "Bizaxl Finance")
cards = json.loads(ws.content) if ws.content else []
print(f"\n✅ Workspace restored!")
print(f"   Cards: {len(cards)}")
print(f"   Links: {len(ws.links)}")
