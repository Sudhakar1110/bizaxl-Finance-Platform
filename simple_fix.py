"""
Simple Workspace Fix - Run in bench console
bench --site finance.bizaxl.local console
Then paste ALL this code
"""
import frappe

# 1. Delete existing workspace
if frappe.db.exists("Workspace", "Bizaxl Finance"):
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = 'Bizaxl Finance'")
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = 'Bizaxl Finance'")
    frappe.db.commit()
    print("Deleted old workspace")

# 2. Get existing DocTypes
existing = set(frappe.db.get_all('DocType', pluck='name'))
print(f"Found {len(existing)} DocTypes")

# 3. Create workspace with SQL (bypass ORM validation)
frappe.db.sql("""
    INSERT INTO `tabWorkspace` (
        name, doctype, title, label, module, icon, is_default, is_standard,
        is_hidden, public, sequence_id, owner, creation, modified
    ) VALUES (
        'Bizaxl Finance', 'Workspace', 'Bizaxl Finance', 'Bizaxl Finance',
        'Bizaxl Finance', 'credit-card', 1, 0, 0, 1, 1.0, 'Administrator',
        NOW(), NOW()
    )
""")

# 4. Cards content
cards = [
    "Lead & DSA Management", "Customer Management", "Banking & Accounts",
    "Payments & Bills", "Investments", "Loan Management", "Insurance",
    "Credit Management", "Portfolio & Goals", "Foundation", "Gold Loan",
    "Microfinance", "Vehicle Loan", "Home Loan", "Business Loan",
    "Education Loan", "BNPL", "Invoice Finance", "Chit Fund",
    "Consumer Finance", "Collections & Recovery", "Risk & Compliance",
    "Accounting", "Integrations & Settings"
]

card_content = []
for c in cards:
    card_content.append(f'{{"type":"card","data":{{"card_name":"{c}","col":4}},"hidden":0}}')

frappe.db.sql("UPDATE `tabWorkspace` SET content = %s WHERE name = 'Bizaxl Finance'", 
              f"[{','.join(card_content)}]")
frappe.db.commit()

print(f"Created {len(cards)} cards")

# 5. Add links (only valid ones)
links_to_add = [
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
    ("Link", "UPI IDs", "UPI ID", "DocType"),
    ("Card Break", "Payments & Bills", "", ""),
    ("Link", "Bill Payments", "Bill Payment", "DocType"),
    ("Link", "Mobile Recharges", "Mobile Recharge", "DocType"),
    ("Card Break", "Investments", "", ""),
    ("Link", "Investment Accounts", "Investment Account", "DocType"),
    ("Link", "Mutual Funds", "Mutual Fund", "DocType"),
    ("Link", "Fixed Deposits", "Fixed Deposit", "DocType"),
    ("Card Break", "Loan Management", "", ""),
    ("Link", "Loan Products", "Loan Product", "DocType"),
    ("Link", "Loan Applications", "Loan Application", "DocType"),
    ("Link", "Loan Disbursements", "Loan Disbursement", "DocType"),
    ("Link", "Loan Repayments", "Loan Repayment", "DocType"),
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
for ltype, label, link_to, link_type in links_to_add:
    if link_type == "DocType" and link_to and link_to not in existing:
        continue
    frappe.db.sql("""
        INSERT INTO `tabWorkspace Link` (
            name, doctype, parent, parentfield, parenttype, type, label, link_to, link_type, hidden
        ) VALUES (
            %(name)s, 'Workspace Link', 'Bizaxl Finance', 'links', 'Workspace',
            %(type)s, %(label)s, %(link_to)s, %(link_type)s, 0
        )
    """, {"name": f"link_{link_count}", "type": ltype, "label": label, "link_to": link_to, "link_type": link_type})
    link_count += 1

frappe.db.commit()

# 6. Clear cache
frappe.cache().delete_value("workspace:data:Bizaxl Finance")
frappe.cache().delete_key("bootinfo")

print(f"✅ Done! Created {len(cards)} cards and {link_count} links")
print("Clear browser cache and refresh!")
