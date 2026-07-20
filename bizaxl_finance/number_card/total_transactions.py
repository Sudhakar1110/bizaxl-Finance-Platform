from __future__ import unicode_literals
import frappe

def get_data():
    return {
        "fieldname": "name",
        "result": frappe.db.count("Transaction", filters={"docstatus": 1}),
        "function": "Count",
        "color": "#00897b",
    }
