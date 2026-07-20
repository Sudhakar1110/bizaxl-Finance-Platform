# Bizaxl Finance Platform

A comprehensive financial services platform built on **Frappe Framework v15+** and **ERPNext v15+**, inspired by the JioFinance application.

## Features

### Banking & Accounts
- Digital bank account management
- UPI ID management
- Transaction tracking with full audit trail
- Payment methods configuration
- Account balance monitoring

### Payments & Bills
- Bill payments (Electricity, Water, Gas, DTH, Broadband, etc.)
- Mobile recharges (Prepaid/Postpaid)
- FASTag recharges
- Recurring payment support
- Auto-pay configuration

### Investments
- Mutual fund portfolio tracking
- Fixed deposit management
- Digital gold investments
- Investment account management
- SIP/STP tracking
- Investment goals planning

### Loan Management
- Multiple loan products (Personal, Home, Auto, Education, Business, etc.)
- End-to-end loan lifecycle (Application → Approval → Disbursement → Repayment)
- EMI calculation with PMT formula
- Collateral management
- Co-applicant support

### Insurance
- Insurance products catalog
- Policy management
- Premium payment tracking
- Claims management
- Nominee management
- Maturity alerts

### Credit Management
- Credit score tracking (CIBIL, Experian, Equifax, CRIF)
- Credit score history
- Credit score improvement goals
- Score range classification

### Portfolio Management
- Consolidated portfolio view
- Asset allocation
- Portfolio performance tracking
- Financial goals planning
- Asset class configuration

### Customer Management
- Comprehensive customer profiles
- KYC document management
- Customer nominations
- Communication history
- Risk profiling

## Installation

### Prerequisites
- Frappe Framework v15+
- ERPNext v15+

### Steps

```bash
# Navigate to bench directory
cd ~/frappe-bench

# Get the app
bench get-app https://github.com/Sudhakar1110/bizaxl-Finance-Platform.git

# Install on site
bench --site yoursite.com install-app bizaxl_finance

# Build assets
bench build

# Migrate
bench --site yoursite.com migrate
```

## Modules

| Module | Description |
|--------|-------------|
| Customer Management | Customer profiles, KYC, nominations |
| Banking | Bank accounts, UPI, transactions |
| Payments | Bill payments, recharges |
| Investments | Mutual funds, FD, digital gold |
| Loans | Loan products, applications, disbursements |
| Insurance | Policies, claims, premiums |
| Credit Management | Credit scores, reports |
| Portfolio Management | Holdings, goals, asset allocation |

## Roles

| Role | Access Level |
|------|-------------|
| Banking Manager | Full banking operations |
| Payments Manager | Payment operations |
| Investment Manager | Investment operations |
| Loan Manager | Loan operations |
| Insurance Manager | Insurance operations |
| Credit Analyst | Credit management |
| Customer Service Representative | Customer support |
| Compliance Officer | Read-only compliance |
| Customer | Portal access |

## API Endpoints

The platform exposes REST APIs for all major operations:

- `/api/method/bizaxl_finance.api.get_customer_dashboard`
- `/api/method/bizaxl_finance.api.get_recent_transactions`
- `/api/method/bizaxl_finance.api.get_portfolio_summary`
- `/api/method/bizaxl_finance.api.get_loan_summary`
- `/api/method/bizaxl_finance.api.get_insurance_summary`
- `/api/method/bizaxl_finance.api.initiate_upi_transfer`
- `/api/method/bizaxl_finance.api.initiate_bill_payment`

## License

MIT
