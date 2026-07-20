from __future__ import unicode_literals
import frappe

def get_data():
    return {
        "fieldname": "name",
        "result": frappe.db.count("Insurance Policy", filters={"status": "Active"}),
        "function": "Count",
        "color": "#2e7d32",
    }
