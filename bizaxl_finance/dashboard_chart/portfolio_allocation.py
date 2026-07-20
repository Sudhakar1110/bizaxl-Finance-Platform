import frappe

def get_data():
    data = frappe.db.sql("""
        SELECT asset_type AS label, COALESCE(SUM(current_value), 0) AS value
        FROM `tabPortfolio Holding`
        WHERE status = 'Active'
        GROUP BY asset_type
        ORDER BY value DESC
    """, as_dict=True)

    return {
        "labels": [d.label for d in data],
        "datasets": [{"values": [d.value for d in data]}],
        "type": "pie",
        "colors": ["#1a73e8", "#00897b", "#7b1fa2", "#e65100", "#2e7d32", "#f9a825", "#37474f"],
    }
