"""
Simple Workspace Creator - Auto-runs on page load
https://finance.bizaxl.local/create-workspace
"""

import frappe
import json

no_cache = 1

@frappe.whitelist()
def create_workspace():
    result = {"success": False, "message": "", "cards": 0, "links": 0}
    
    try:
        # Get existing DocTypes
        existing = set(frappe.db.get_all('DocType', pluck='name'))
        
        # 24 Cards
        cards = [
            "Lead & DSA Management", "Customer Management", "Banking & Accounts",
            "Payments & Bills", "Investments", "Loan Management", "Insurance",
            "Credit Management", "Portfolio & Goals", "Foundation", "Gold Loan",
            "Microfinance", "Vehicle Loan", "Home Loan", "Business Loan",
            "Education Loan", "BNPL", "Invoice Finance", "Chit Fund",
            "Consumer Finance", "Collections & Recovery", "Risk & Compliance",
            "Accounting", "Integrations & Settings"
        ]
        
        card_items = []
        for c in cards:
            card_items.append(f'{{"type":"card","data":{{"card_name":"{c}","col":4}},"hidden":0}}')
        content = "[" + ",".join(card_items) + "]"
        
        # Links (only Card Breaks + links that exist)
        all_links = [
            ("Card Break", "Lead & DSA Management", "", ""),
            ("Link", "Leads", "Lead", "DocType"),
            ("Link", "DSA Masters", "DSA Master", "DocType"),
            ("Card Break", "Customer Management", "", ""),
            ("Link", "Bizaxl Customers", "Bizaxl Customer", "DocType"),
            ("Link", "KYC Documents", "KYC Document", "DocType"),
            ("Link", "Customer Communications", "Customer Communication", "DocType"),
            ("Card Break", "Banking & Accounts", "", ""),
            ("Link", "Bank Accounts", "Bank Account", "DocType"),
            ("Link", "Transactions", "Transaction", "DocType"),
            ("Card Break", "Payments & Bills", "", ""),
            ("Link", "Bill Payments", "Bill Payment", "DocType"),
            ("Link", "Mobile Recharges", "Mobile Recharge", "DocType"),
            ("Card Break", "Investments", "", ""),
            ("Link", "Investment Accounts", "Investment Account", "DocType"),
            ("Card Break", "Loan Management", "", ""),
            ("Link", "Loan Products", "Loan Product", "DocType"),
            ("Link", "Loan Applications", "Loan Application", "DocType"),
            ("Link", "Loan Disbursements", "Loan Disbursement", "DocType"),
            ("Card Break", "Insurance", "", ""),
            ("Link", "Insurance Products", "Insurance Product", "DocType"),
            ("Link", "Insurance Policies", "Insurance Policy", "DocType"),
            ("Card Break", "Credit Management", "", ""),
            ("Link", "Credit Reports", "Credit Report", "DocType"),
            ("Card Break", "Collections & Recovery", "", ""),
            ("Link", "Collection Records", "Collection Record", "DocType"),
            ("Card Break", "Risk & Compliance", "", ""),
            ("Link", "AML Screenings", "AML Screening", "DocType"),
            ("Link", "Fraud Alerts", "Fraud Alert", "DocType"),
        ]
        
        # Delete existing workspace
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = 'Bizaxl Finance'")
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = 'Bizaxl Finance'")
        frappe.db.commit()
        
        # Get columns
        cols = [r[0] for r in frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`")]
        
        # Build insert with all possible fields
        insert_cols = []
        vals = []
        
        field_map = {
            "name": "Bizaxl Finance",
            "title": "Bizaxl Finance",
            "label": "Bizaxl Finance",
            "module": "Bizaxl Finance",
            "icon": "credit-card",
            "public": 1,
            "sequence_id": 1.0,
            "owner": "Administrator",
            "creation": frappe.utils.now(),
            "modified": frappe.utils.now(),
            "content": content,
            "is_standard": 0,
            "is_hidden": 0,
            "is_default": 1,
            "category": "Modules",
            "restrict_to_domain": "",
            "developer_mode_only": 0,
            "disable_user_customization": 0,
            "extends": "",
            "extends_another_page": 0,
            "hide_custom": 0,
            "idx": 0,
            "parent_page": "",
        }
        
        for col in cols:
            if col in field_map:
                insert_cols.append(col)
                vals.append(field_map[col])
        
        cols_str = ", ".join([f"`{c}`" for c in insert_cols])
        vals_str = ", ".join(["%s"] * len(insert_cols))
        frappe.db.sql(f"INSERT INTO `tabWorkspace` ({cols_str}) VALUES ({vals_str})", vals)
        
        # Add links
        link_cols = [r[0] for r in frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Link`")]
        link_insert_cols = ["name", "parent", "parentfield", "parenttype", "type", "label", "link_to", "link_type", "hidden", "is_query_report", "onboard", "dependencies", "link_count"]
        link_insert_cols = [c for c in link_insert_cols if c in link_cols]
        
        link_count = 0
        for idx, (ltype, label, link_to, link_type) in enumerate(all_links):
            if link_type == "DocType" and link_to and link_to not in existing:
                continue
            
            link_vals = []
            for c in link_insert_cols:
                if c == "name": link_vals.append(f"wsl_{link_count}")
                elif c == "parent": link_vals.append("Bizaxl Finance")
                elif c == "parentfield": link_vals.append("links")
                elif c == "parenttype": link_vals.append("Workspace")
                elif c == "type": link_vals.append(ltype)
                elif c == "label": link_vals.append(label)
                elif c == "link_to": link_vals.append(link_to)
                elif c == "link_type": link_vals.append(link_type)
                elif c == "hidden": link_vals.append(0)
                elif c == "is_query_report": link_vals.append(0)
                elif c == "onboard": link_vals.append(0)
                elif c == "dependencies": link_vals.append("")
                elif c == "link_count": link_vals.append(0)
            
            cols_str = ", ".join([f"`{c}`" for c in link_insert_cols])
            vals_str = ", ".join(["%s"] * len(link_insert_cols))
            frappe.db.sql(f"INSERT INTO `tabWorkspace Link` ({cols_str}) VALUES ({vals_str})", link_vals)
            link_count += 1
        
        frappe.db.commit()
        frappe.cache().delete_key("bootinfo")
        
        result["success"] = True
        result["cards"] = len(cards)
        result["links"] = link_count
        result["message"] = f"Created {len(cards)} cards, {link_count} links"
        
    except Exception as e:
        result["message"] = str(e)
    
    return result

def get_context(context):
    context.result = create_workspace()
    context.title = "Creating Workspace"
