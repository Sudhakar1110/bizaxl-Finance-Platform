"""Run: bench --site finance.bizaxl.local console
Then paste this code:"""
import frappe
import json
ws = frappe.get_doc("Workspace", "Bizaxl Finance")
print(f"Content length: {len(ws.content) if ws.content else 0}")
print(f"Content: {ws.content[:300] if ws.content else 'EMPTY'}...")
cards = json.loads(ws.content) if ws.content else []
print(f"Cards: {len(cards)}")
print(f"Links: {len(ws.links)}")
