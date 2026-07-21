"""Run in bench console"""
import frappe
ws = frappe.get_doc("Workspace", "Bizaxl Finance")
print(f"name: {ws.name}")
print(f"title: {ws.title}")
print(f"module: {ws.module}")
print(f"is_default: {ws.is_default}")
print(f"public: {ws.public}")
print(f"is_hidden: {ws.is_hidden}")
print(f"sequence_id: {ws.sequence_id}")
print(f"icon: {ws.icon}")
print(f"parent_page: '{ws.parent_page}'")
