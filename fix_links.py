"""
Run this in bench console to fix workspace links:
bench --site finance.bizaxl.local console

Then paste the entire content of this file.
"""

import frappe
import json

# Get all existing DocTypes
existing_doctypes = set(frappe.db.get_all('DocType', pluck='name'))

# Get all existing Reports
existing_reports = set(frappe.db.get_all('Report', pluck='name'))

# Get workspace
ws = frappe.get_doc("Workspace", "Bizaxl Finance")

removed_links = []
kept_links = []

for link in ws.links:
    link_to = link.get('link_to', '')
    link_type = link.get('link_type', '')
    
    if link_type == 'DocType' and link_to:
        if link_to not in existing_doctypes:
            removed_links.append(f"[DocType] {link_to}")
            link.parent = None  # Mark for removal
        else:
            kept_links.append(link_to)
    elif link_type == 'Report' and link_to:
        if link_to not in existing_reports:
            removed_links.append(f"[Report] {link_to}")
            link.parent = None
        else:
            kept_links.append(link_to)
    elif link_type == 'Card Break' or not link_to:
        kept_links.append(f"[Card Break] {link.get('label', '')}")

# Remove broken links
ws.links = [l for l in ws.links if l.parent is not None]

print(f"Removed {len(removed_links)} broken links:")
for r in removed_links:
    print(f"  - {r}")

print(f"\nKept {len(kept_links)} valid links")

# Save with bypass
ws.flags.ignore_links = True
ws.flags.ignore_mandatory = True
ws.save(ignore_permissions=True)
frappe.db.commit()

print("\n✅ Workspace updated!")
print(f"   Links now: {len(ws.links)}")
