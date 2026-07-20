from __future__ import unicode_literals
import frappe

def get_data():
    data = frappe.db.sql("""
        SELECT loan_type AS label, COALESCE(SUM(loan_amount), 0) AS value
        FROM `tabLoan Application`
        WHERE status IN ('Disbursed', 'Approved')
        GROUP BY loan_type
        ORDER BY value DESC
    """, as_dict=True)

    return {
        "labels": [d.label for d in data],
        "datasets": [{"values": [d.value for d in data]}],
        "type": "bar",
        "colors": ["#e65100", "#bf360c", "#ef6c00", "#f57c00"],
    }
