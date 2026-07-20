from __future__ import unicode_literals
import frappe

def get_data():
    return {
        "fieldname": "name",
        "result": frappe.db.count("Loan Application", filters={"status": "Disbursed"}),
        "function": "Count",
        "color": "#e65100",
    }
