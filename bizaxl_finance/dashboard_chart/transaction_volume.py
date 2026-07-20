from __future__ import unicode_literals
import frappe

def get_data():
    data = frappe.db.sql("""
        SELECT DATE(transaction_date) AS date,
               COUNT(*) AS count,
               COALESCE(SUM(amount), 0) AS total_amount
        FROM `tabTransaction`
        WHERE docstatus = 1
            AND DATE(transaction_date) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY DATE(transaction_date)
        ORDER BY date ASC
    """, as_dict=True)

    return {
        "labels": [d.date.strftime('%d-%m') if d.date else '' for d in data],
        "datasets": [
            {"name": "Transaction Count", "values": [d.count for d in data]},
            {"name": "Transaction Volume", "values": [d.total_amount for d in data]},
        ],
        "type": "line",
        "colors": ["#1a73e8", "#00897b"],
    }
