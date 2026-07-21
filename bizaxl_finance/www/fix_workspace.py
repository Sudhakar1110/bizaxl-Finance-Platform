"""
Auto Fix Workspace - Visit this URL to fix:
https://finance.bizaxl.local/fix-workspace
"""

import frappe
import json

no_cache = 1

@frappe.whitelist()
def fix():
    result = {"success": False, "message": "", "cards": 0, "links": 0}
    
    try:
        # Delete old workspace
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = 'Bizaxl Finance'")
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = 'Bizaxl Finance'")
        frappe.db.commit()
        
        # Get valid DocTypes
        existing = set(frappe.db.get_all('DocType', pluck='name'))
        
        # Create workspace
        frappe.db.sql("""
            INSERT INTO `tabWorkspace` (name, doctype, title, label, module, icon, is_default, is_standard, is_hidden, public, sequence_id, owner, creation, modified)
            VALUES ('Bizaxl Finance', 'Workspace', 'Bizaxl Finance', 'Bizaxl Finance', 'Bizaxl Finance', 'credit-card', 1, 0, 0, 1, 1.0, 'Administrator', NOW(), NOW())
        """)
        
        # Add 24 cards
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
        frappe.db.sql("UPDATE `tabWorkspace` SET content = %s WHERE name = 'Bizaxl Finance'", content)
        
        # Add links
        links = [
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
        
        link_count = 0
        for ltype, label, link_to, link_type in links:
            if link_type == "DocType" and link_to not in existing:
                continue
            name = f"ws_link_{link_count}"
            frappe.db.sql("""
                INSERT INTO `tabWorkspace Link` (name, doctype, parent, parentfield, parenttype, type, label, link_to, link_type, hidden)
                VALUES (%s, 'Workspace Link', 'Bizaxl Finance', 'links', 'Workspace', %s, %s, %s, %s, 0)
            """, (name, ltype, label, link_to, link_type))
            link_count += 1
        
        frappe.db.commit()
        frappe.cache().delete_key("bootinfo")
        
        result["success"] = True
        result["cards"] = len(cards)
        result["links"] = link_count
        result["message"] = f"Workspace fixed with {len(cards)} cards and {link_count} links!"
        
    except Exception as e:
        result["message"] = str(e)
    
    return result

def get_context(context):
    # Auto-run the fix
    context.result = fix()
    context.title = "Fix Workspace"
