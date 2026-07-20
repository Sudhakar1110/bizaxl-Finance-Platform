import frappe

def get_data():
    return {
        "fieldname": "name",
        "transactions": [],
        "result": frappe.db.count("Bizaxl Customer", filters={"is_active": 1}),
        "function": "Count",
        "filters": [],
        "aggregate_function_based_on": "",
        "color": "#1a73e8",
    }
