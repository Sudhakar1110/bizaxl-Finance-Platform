app_name = "bizaxl_finance"
app_title = "Bizaxl Finance Platform"
app_publisher = "Bizaxl Technologies"
app_description = "Complete Financial Services Platform — 12 Lending Verticals: NBFC, MFI, Gold Loan, Vehicle Loan, Home Loan, Personal Loan, Business Loan, Education Loan, BNPL, Invoice Finance, Chit Fund, Consumer Finance"
app_email = "info@bizaxl.com"
app_license = "MIT"
app_version = "1.0.0"

# ── Required Apps ─────────────────────────────────────────────────────────────
required_apps = ["frappe", "erpnext"]

# ── Asset Configuration ────────────────────────────────────────────────────────
app_include_js = "/assets/bizaxl_finance/js/bizaxl_finance.js"
app_include_css = "/assets/bizaxl_finance/css/bizaxl_finance.css"

# ── Portal Configuration ──────────────────────────────────────────────────────
portal_menu_items = [
    {"title": "My Accounts", "route": "/bizaxl-portal/accounts", "role": "Customer"},
    {"title": "My Investments", "route": "/bizaxl-portal/investments", "role": "Customer"},
    {"title": "My Loans", "route": "/bizaxl-portal/loans", "role": "Customer"},
    {"title": "My Insurance", "route": "/bizaxl-portal/insurance", "role": "Customer"},
    {"title": "Pay Bills", "route": "/bizaxl-portal/payments", "role": "Customer"},
]

# ── Fixtures ──────────────────────────────────────────────────────────────────
fixtures = [
    {"dt": "Role", "filters": [["role_name", "in", [
        "Banking Manager",
        "Payments Manager",
        "Investment Manager",
        "Loan Manager",
        "Insurance Manager",
        "Credit Analyst",
        "Customer",
        "Customer Service Representative",
        "Compliance Officer",
        "System Admin",
        "Credit Officer",
        "Collection Officer",
        "Gold Appraiser",
        "Branch Manager",
        "Auditor",
        "Relationship Manager",
        "Field Officer",
        "Chit Foreman",
    ]]}]},
    "Custom Field",
    "Property Setter",
    {"dt": "Module Def", "filters": [["module_name", "=", "Bizaxl Finance"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Banking"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Payments"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Investments"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Loans"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Insurance"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Credit Management"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Portfolio Management"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Customer Management"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Foundation"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "NBFC Lending"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Gold Loan"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Microfinance"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Vehicle Loan"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Home Loan"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Business Loan"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Education Loan"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "BNPL"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Invoice Finance"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Chit Fund"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Consumer Finance"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Collections"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Risk & Compliance"]]},
    {"dt": "Module Def", "filters": [["module_name", "=", "Accounting"]]},
    {"dt": "Workspace", "filters": [["name", "=", "Bizaxl Finance"]]},
]

# ── Custom Roles ──────────────────────────────────────────────────────────────
roles = [
    {"role_name": "System Admin", "desk_access": 1},
    {"role_name": "Credit Officer", "desk_access": 1},
    {"role_name": "Collection Officer", "desk_access": 1},
    {"role_name": "Gold Appraiser", "desk_access": 1},
    {"role_name": "Branch Manager", "desk_access": 1},
    {"role_name": "Auditor", "desk_access": 1},
    {"role_name": "Relationship Manager", "desk_access": 1},
    {"role_name": "Field Officer", "desk_access": 1},
    {"role_name": "Chit Foreman", "desk_access": 1},
    {"role_name": "Banking Manager", "desk_access": 1},
    {"role_name": "Payments Manager", "desk_access": 1},
    {"role_name": "Investment Manager", "desk_access": 1},
    {"role_name": "Loan Manager", "desk_access": 1},
    {"role_name": "Insurance Manager", "desk_access": 1},
    {"role_name": "Credit Analyst", "desk_access": 1},
    {"role_name": "Customer", "desk_access": 0},
    {"role_name": "Customer Service Representative", "desk_access": 1},
    {"role_name": "Compliance Officer", "desk_access": 1},
]

# ── Scheduler Events ──────────────────────────────────────────────────────────
scheduler_events = {
    "daily": [
        "bizaxl_finance.tasks.process_due_premiums",
        "bizaxl_finance.tasks.calculate_loan_interest",
        "bizaxl_finance.tasks.update_credit_scores",
        "bizaxl_finance.tasks.process_recurring_bill_payments",
        "bizaxl_finance.tasks.send_due_payment_reminders",
    ],
    "weekly": [
        "bizaxl_finance.tasks.generate_portfolio_summaries",
        "bizaxl_finance.tasks.generate_customer_statements",
    ],
    "monthly": [
        "bizaxl_finance.tasks.generate_maturity_alerts",
        "bizaxl_finance.tasks.calculate_commission_payouts",
    ],
}

# ── Dashboard Configuration ──────────────────────────────────────────────────
override_doctype_dashboards = {}

# ── Document Events ───────────────────────────────────────────────────────────
# DocType events are handled via standard Frappe controller methods
# (before_save, before_submit, on_submit, etc.) in each DocType's Python file
doc_events = {}

# ── Website ───────────────────────────────────────────────────────────────────
website_route_rules = [
    {"from_route": "/bizaxl-portal", "to_route": "bizaxl_portal"},
]

# ── Jinja ─────────────────────────────────────────────────────────────────────
jinja = {
    "methods": [],
    "filters": [],
}

# ── Permissions ───────────────────────────────────────────────────────────────
permission_query_conditions = {
    "Bank Account": "bizaxl_finance.permissions.get_bank_account_permission_query_conditions",
    "Transaction": "bizaxl_finance.permissions.get_transaction_permission_query_conditions",
    "Loan Application": "bizaxl_finance.permissions.get_loan_permission_query_conditions",
    "Insurance Policy": "bizaxl_finance.permissions.get_insurance_permission_query_conditions",
}

has_permission = {
    "Bank Account": "bizaxl_finance.permissions.has_bank_account_permission",
    "Transaction": "bizaxl_finance.permissions.has_transaction_permission",
}
