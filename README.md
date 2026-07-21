# 🏦 Bizaxl Finance Platform

**Complete Financial Services Platform — 12 Lending Verticals**

Built on **Frappe Framework v15+** and **ERPNext v15+**, Bizaxl Finance is a single platform covering all 12 lending verticals active in the Indian financial services market — NBFC, Microfinance (MFI/JLG/SHG), Gold Loan, Vehicle Loan, Home Loan, Personal Loan, Business Loan, Education Loan, Consumer Finance, BNPL, Invoice Financing, and Chit Fund.

> **Three core principles:**
> 1. Every vertical has its own purpose-built workflow — not a generic loan module stretched to fit
> 2. Compliance is built in, not bolted on — RBI, NHB, NABARD, ROC, and FIU-IND requirements are automated
> 3. The same platform handles a 20-member chit group and a Rs.500 Cr NBFC portfolio without configuration changes

---

## 📊 Platform Overview

| Metric | Count |
|--------|-------|
| **DocTypes** | **106** |
| **Lending Verticals** | **12** |
| **API Integrations** | **18** |
| **User Roles** | **18** |
| **Script Reports** | **11** |
| **Workspace Cards** | **24** |
| **Scheduler Events** | **12** |

---

## 📦 12 Lending Verticals

| # | Vertical | Core DocTypes | 
|---|----------|---------------|
| 1 | 🏛️ **NBFC Lending** | NBFC Loan Application, Loan Application, Credit Committee Decision |
| 2 | 🤝 **Microfinance (MFI)** | MFI Center, JLG Group, MFI Member, Group Disbursement, MFI Collection, Household Form |
| 3 | 🥇 **Gold Loan** | Gold Pledge, Gold Item, Gold Auction, Vault Register, Auctioneer Register |
| 4 | 🚗 **Vehicle Loan** | Vehicle Detail, Dealer Master, Vehicle Repossession |
| 5 | 🏠 **Home Loan / LAP** | Property Detail, Tranche Disbursement, PMAY Subsidy, Balance Transfer, Legal Opinion, Engineer Certificate |
| 6 | 👤 **Personal Loan** | Personal Loan Application, Scorecard Config |
| 7 | 💼 **Business / MSME Loan** | Business Profile, Collateral Register, Loan Covenant, Covenant Monitoring Log |
| 8 | 🎓 **Education Loan** | Institution Master, Course Detail, CSIS Application |
| 9 | 🛒 **BNPL** | BNPL Limit, BNPL Transaction |
| 10 | 🧾 **Invoice Finance** | Anchor Master, Invoice Finance |
| 11 | 🏆 **Chit Fund** | Chit Group, Chit Subscriber, Chit Auction, Chit ROC Return |
| 12 | 📦 **Consumer Finance** | Retailer Master, POS Transaction |

---

## 🏗️ 9 Core Modules

### 1. 🏛️ Foundation Layer
Company configuration, branch master, product factory, interest rate engine, charge rules, regulatory settings — the base upon which all verticals are built.

**DocTypes:** `Company Config`, `Branch Master`, `Product Factory`, `Interest Rate Engine`, `Charge Rule`

### 2. 👤 Customer Acquisition
CRM lead pipeline, digital onboarding, eKYC/Video KYC, Aadhaar/PAN verification, DSA management.

**DocTypes:** `Lead`, `Bizaxl Customer`, `KYC Document`, `Video KYC Session`, `DSA Master`, `Customer Communication`, `Customer Nomination`

### 3. 📝 Loan Origination System (LOS)
BPM-configured origination for all 12 verticals. Credit assessment, bureau pull, FOIR, risk grading (A1-D), committee approval workflow, e-sign, sanction letter.

**DocTypes:** `Loan Application`, `Personal Loan Application`, `NBFC Loan Application`, `Credit Committee Decision`, `Scorecard Config`, `Sanction Letter`

### 4. 💼 Loan Management System (LMS)
Full loan lifecycle post-sanction: EMI schedules, interest calculation, prepayment, restructuring, rate reset, moratorium, co-lending split, securitization.

**DocTypes:** `EMI Schedule`, `Prepayment Request`, `Loan Restructure`, `Rate Reset Log`, `Loan Accounting`

### 5. 💸 Collections & Recovery
NACH auto-debit, UPI AutoPay, DPD tracking, NPA/PAR classification, recovery stages, SARFAESI, write-off.

**DocTypes:** `Collection Record`, `NACH Mandate`, `NPA Classification`, `SARFAESI Case`, `Write-off`

### 6. 🛡️ Risk & Compliance
AML/KYC screening, fraud detection (5 alert types), RBI/NHB/NABARD/ROC/FIU-IND reporting, audit trail.

**DocTypes:** `AML Screening`, `Fraud Alert`, `Regulatory Report`

### 7. 📊 Accounting & Treasury
Native GL engine, fund management, co-lending P&L split, provisioning, interest income accrual, ALM reporting.

**DocTypes:** `GL Settings`, `Loan Accounting`, `Fund Account`, `Co-lending Partnership`, `Provisioning Rule`

### 8. 🏆 Chit Fund Engine
Chit group management, monthly subscription, auction engine, foreman commission, dividend distribution, subscriber ledger, ROC returns.

**DocTypes:** `Chit Group`, `Chit Subscriber`, `Chit Auction`, `Chit ROC Return`

### 9. 📱 Mobile & Field Apps
Customer mobile app (Android/iOS), field officer app (offline-capable), MFI center meeting app with GPS stamp, collection tracker, offline sync.

---

## 🔌 18 API Integrations

All integrations follow a **stub-to-live pattern** — they work without API keys in simulated mode, and switch to live automatically when credentials are entered in Integration Settings.

| # | API | Purpose | Module |
|---|-----|---------|--------|
| 1 | 🪪 **UIDAI — Aadhaar eKYC** | OTP-based eKYC, Offline XML, address pre-fill | KYC |
| 2 | 💳 **NSDL — PAN Verification** | PAN validate + name/DOB match + CKYC | KYC |
| 3 | 📊 **Bureau (CIBIL/Experian/CRIF/Equifax)** | Consumer + commercial + MFI bureau | Credit |
| 4 | 📁 **Account Aggregator (AA)** | Sahamati TSP, 12M bank statement fetch, FOIR | Income |
| 5 | 🇮🇳 **NPCI — UPI/IMPS/NEFT/RTGS** | Full payment rail execution | Payments |
| 6 | 🔁 **NACH / UPI AutoPay** | eNACH mandate registration + execution | Collections |
| 7 | 📩 **SMS / WhatsApp / Email** | MSG91, Twilio, WhatsApp Business alerts | Notifications |
| 8 | 🛡️ **Sanctions (OFAC/UN/PEP)** | Real-time AML screening | Compliance |
| 9 | ✍️ **e-Sign / DigiLocker** | Aadhaar-based e-Sign for loan agreements | Legal |
| 10 | 📋 **GSTN API** | GST return fetch (GSTR-1 + GSTR-3B) | MSME |
| 11 | 🥇 **MCX — Live Gold Rate** | Real-time gold rate for LTV calculation | Gold Loan |
| 12 | 🧾 **TReDS Platform** | Invoice financing secondary market | Invoice Finance |
| 13 | 🚗 **Parivahan — RC Hypothecation** | Vehicle RC status + hypothecation | Vehicle Loan |
| 14 | 🏛️ **CERSAI — Mortgage Registry** | Immovable property mortgage registration | Home Loan |
| 15 | 🎓 **CSIS — Education Subsidy** | Central Interest Subsidy Scheme | Education Loan |
| 16 | 🏘️ **PMAY / NHB** | CLSS eligibility check + nodal submission | Home Loan |
| 17 | 📱 **Video KYC (In-app)** | In-app Video KYC with session recording | KYC |
| 18 | 🤖 **AI/ML Scorecard Engine** | Configurable ML scorecard per vertical | Credit |

---

## 👥 18 User Roles

| Role | Scope | Key Access |
|------|-------|------------|
| **System Admin** | All modules, all branches | Full CRUD on all 106+ DocTypes, integration settings |
| **Branch Manager** | Own branch, all verticals | Approve loans, payments, reports, override within limits |
| **Relationship Manager/DSA** | Own assigned customers | Create leads, applications, track commission |
| **Credit Officer** | All loan applications | Underwrite, risk grade, bureau pull, sanction/refer |
| **Field Officer (MFI)** | Assigned centers/groups | Center meetings, member KYC, collection, offline sync |
| **Collection Officer** | Assigned delinquent portfolio | DPD view, field collection, recovery, legal escalation |
| **Compliance Officer** | All accounts (read+compliance) | AML review, fraud alerts, KYC sign-off, regulatory reports |
| **Auditor** | All modules (read-only) | View all transactions, reports, audit trail, export |
| **Gold Appraiser** | Gold Loan only | Gold item entry, purity assessment, vault update, auction |
| **Chit Foreman** | Assigned chit groups | Subscription collection, auction, dividend, subscriber ledger |
| **Loan Manager** | Loan operations | Full loan lifecycle management |
| **Insurance Manager** | Insurance operations | Policy, claims, premium management |
| **Investment Manager** | Investment operations | Mutual funds, FD, digital gold management |
| **Banking Manager** | Banking operations | Account, transaction, UPI management |
| **Payments Manager** | Payment operations | Bill payments, recharges management |
| **Credit Analyst** | Credit management | Credit reports, score analysis |
| **Customer Service Rep** | Customer support | Profile management, communications |
| **Customer** | Own accounts only | Self-service portal, balance view, EMI payment |

---

## 📂 Complete DocType List by Module

### Banking (5)
`Banking Settings`, `Bank Account`, `Payment Method`, `Transaction`, `UPI ID`

### BNPL (2)
`BNPL Limit`, `BNPL Transaction`

### Business Loan (4)
`Business Profile`, `Collateral Register`, `Covenant Monitoring Log`, `Loan Covenant`

### Chit Fund (4)
`Chit Auction`, `Chit Group`, `Chit ROC Return`, `Chit Subscriber`

### Collections (5)
`Collection Record`, `NACH Mandate`, `NPA Classification`, `SARFAESI Case`, `Write-off`

### Consumer Finance (2)
`POS Transaction`, `Retailer Master`

### Credit Management (3)
`Credit Goal`, `Credit Report`, `Credit Score History`

### Customer Management (7)
`Bizaxl Customer`, `Customer Communication`, `Customer Nomination`, `DSA Master`, `KYC Document`, `Lead`, `Video KYC Session`

### Education Loan (3)
`Course Detail`, `CSIS Application`, `Institution Master`

### Foundation (5)
`Branch Master`, `Charge Rule`, `Company Config`, `Interest Rate Engine`, `Product Factory`

### Gold Loan (5)
`Auctioneer Register`, `Gold Auction`, `Gold Item`, `Gold Pledge`, `Vault Register`

### Home Loan (6)
`Balance Transfer`, `Engineer Certificate`, `Legal Opinion`, `PMAY Subsidy`, `Property Detail`, `Tranche Disbursement`

### Insurance (6)
`Insurance Bundle Tracker`, `Insurance Claim`, `Insurance Nominee`, `Insurance Policy`, `Insurance Product`, `Premium Payment`

### Integrations (8)
`Integration Settings`, `Integration Request`, `OAuth Client`, `OAuth Scope`, `OAuth Bearer Token`, `OAuth Authorization Code`, `Webhook Data`, `Webhook Request Log`

### Investments (6)
`Digital Gold`, `Fixed Deposit`, `Investment Account`, `Investment Goal`, `Mutual Fund`, `Mutual Fund Transaction`

### Invoice Finance (2)
`Anchor Master`, `Invoice Finance`

### Loans (13)
`Credit Committee Decision`, `EMI Schedule`, `Loan Application`, `Loan Collateral`, `Loan Disbursement`, `Loan Product`, `Loan Repayment`, `Loan Restructure`, `Personal Loan Application`, `Prepayment Request`, `Rate Reset Log`, `Sanction Letter`, `Scorecard Config`

### Microfinance (6)
`Group Disbursement`, `Household Form`, `JLG Group`, `MFI Center`, `MFI Collection`, `MFI Member`

### NBFC Lending (1)
`NBFC Loan Application`

### Payments (5)
`Bill Payment`, `Bill Payment Category`, `FASTag Recharge`, `Mobile Recharge`, `Recharge Provider`

### Portfolio Management (4)
`Asset Class`, `Financial Goal`, `Portfolio Holding`, `Portfolio Summary`

### Risk & Compliance (3)
`AML Screening`, `Fraud Alert`, `Regulatory Report`

### Vehicle Loan (3)
`Dealer Master`, `Vehicle Detail`, `Vehicle Repossession`

### Accounting (5)
`Co-lending Partnership`, `Fund Account`, `GL Settings`, `Loan Accounting`, `Provisioning Rule`

---

## 📊 Script Reports (11)

| Report | Module | Description |
|--------|--------|-------------|
| Transaction Register | Banking | All transactions with filters |
| Chit Fund Portfolio | Chit Fund | Chit group performance |
| Collection Efficiency | Collections | Collection recovery rates |
| NPA Portfolio | Collections | NPA breakdown by category |
| Lead Pipeline | Customer Management | Lead funnel analysis |
| Disbursement Report | Foundation | Loan disbursement tracking |
| Gold Loan Portfolio | Gold Loan | Gold loan LTV and aging |
| Home Loan Portfolio | Home Loan | Home loan portfolio analysis |
| Loan Repayment Schedule | Loans | EMI schedule view |
| PAR Portfolio | Microfinance | Portfolio at risk analysis |
| Vehicle Loan Portfolio | Vehicle Loan | Vehicle loan portfolio |

---

## 🚀 Installation

### Prerequisites
- Frappe Framework v15+
- ERPNext v15+

### Steps

```bash
# STEP 1: Get the app with EXPLICIT app name mapping
bench get-app bizaxl_finance https://github.com/Sudhakar1110/bizaxl-Finance-Platform.git --branch main

# STEP 2: Install on your site
bench --site your-site.com install-app bizaxl_finance

# STEP 3: Build assets and migrate
bench build
bench --site your-site.com migrate

# STEP 4: Enable developer mode (if creating new DocTypes)
bench --site your-site.com set-config developer_mode 1
```

### For Existing Installations (Pull Latest Changes)

```bash
cd ~/frappe-bench/apps/bizaxl_finance
git pull origin main
cd ~/frappe-bench
bench --site your-site.com clear-cache
bench --site your-site.com migrate
bench clear-cache
bench restart
```

> **Note:** The workspace auto-syncs to 24 cards after every `bench migrate` via the `after_migrate` hook.

---

## 🔧 Key Features Implemented

### Loan Management
- ✅ FOIR Calculator with auto manual-review flag
- ✅ Risk Grade A1-D (composite scoring: credit + LTV + amount)
- ✅ Processing Fee Engine (auto-fetch from Product, GST@18%)
- ✅ EMI Schedule generation
- ✅ Prepayment Request with recalculation
- ✅ Loan Restructure with audit trail
- ✅ Rate Reset Log for MCLR/repo tracking
- ✅ Step-up EMI for education loans (10% annual increase)

### Gold Loan
- ✅ Real-time LTV calculation (RBI 75% max)
- ✅ Daily LTV monitoring with breach alerts
- ✅ Top-up loan against LTV headroom
- ✅ Gold loan renewal (auto-renew at maturity)
- ✅ Auction workflow with auctioneer tracking
- ✅ Vault register with tag-wise tracking

### Vehicle Loan
- ✅ RC Hypothecation tracking (5 stages: Pending→Submitted→Endorsed→Copy→Released)
- ✅ Parivahan API integration stubs
- ✅ Vehicle repossession with yard inventory
- ✅ Insurance expiry tracking with 30-day alerts
- ✅ Down payment validation per RBI norms

### Home Loan
- ✅ Legal Opinion with title verification
- ✅ Engineer Certificate for construction stages
- ✅ Multi-tranche disbursement linked to construction
- ✅ PMAY CLSS subsidy tracking
- ✅ Balance transfer / top-up for existing customers

### Business / MSME Loan
- ✅ GSTN-based income assessment
- ✅ DSCR calculator (EBITDA/Total Debt Service)
- ✅ Covenant monitoring with auto-compliance checks
- ✅ Collateral register with CERSAI tracking

### Collections
- ✅ NPA auto-classification (SMA-0/1/2 → Sub-standard → Doubtful → Loss)
- ✅ SARFAESI case management
- ✅ NACH/UPI AutoPay mandate setup
- ✅ Write-off management

### Risk & Compliance
- ✅ CRILC report (Rs.5Cr+ exposures)
- ✅ FPC Report (capital adequacy)
- ✅ PSL Report (priority sector computation)
- ✅ FIU-IND CTR/STR filing
- ✅ ALM Report (asset-liability gap)
- ✅ Board Report with portfolio KPIs
- ✅ AML screening with sanctions checks
- ✅ Fraud alert management (5 alert types)

### BNPL
- ✅ Revolving credit limit management
- ✅ Merchant subvention engine (0% EMI)
- ✅ D+2 merchant settlement
- ✅ UPI AutoPay collections

### Chit Fund
- ✅ Auction engine with bid recording
- ✅ Dividend per non-prized subscriber
- ✅ Foreman commission (5% per Chit Funds Act)
- ✅ ROC returns filing

### Invoice Finance
- ✅ GRN matching and duplicate invoice check
- ✅ TReDS platform integration (submit/bid/accept/settle)
- ✅ Recourse/non-recourse funding

---

## 🧪 Features Enhanced (15 Recent Implementations)

| # | Feature | Module | Enhancement |
|---|---------|--------|-------------|
| 1 | FOIR Calculator | Loans | Auto-calc with 50%/55% thresholds, manual review flag |
| 2 | Risk Grade A1-D | Loans | Composite scoring (credit 40% + LTV 30% + amount 30%) |
| 3 | Processing Fee Engine | Loans | Auto-fetch from Loan Product, GST@18% on fee |
| 4 | CRILC Report | Risk & Compliance | Rs.5Cr+ exposure reporting |
| 5 | FPC Report | Risk & Compliance | Capital adequacy computation |
| 6 | PSL Report | Risk & Compliance | 40% target with shortfall |
| 7 | Gold LTV Breach Alert | Gold Loan | Fraud Alert creation, daily monitoring |
| 8 | Gold Top-up Loan | Gold Loan | Headroom calc, auto-pledge creation |
| 9 | RC Hypothecation Tracker | Vehicle Loan | Full 5-stage tracking + Parivahan stubs |
| 10 | Vehicle Yard Inventory | Vehicle Loan | Condition tracking, auction workflow |
| 11 | DSCR Calculator | Business Loan | EBITDA/Debt Service formula |
| 12 | BNPL Subvention Engine | BNPL | Merchant subvention calc |
| 13 | TReDS Integration | Invoice Finance | Submit/bid/accept/settle |
| 14 | Chit Dividend Calc | Chit Fund | Per-member dividend distribution |
| 15 | Step-up EMI | Education Loan | 5-year progressive EMI schedule |

---

## 📁 Project Structure

```
bizaxl_finance/
├── accounting/           # GL, fund management, provisioning
├── banking/              # Bank accounts, UPI, transactions
├── bnpl/                 # Buy Now Pay Later
├── business_loan/        # MSME/Business lending
├── chit_fund/            # Chit fund management
├── collections/          # Collections, NACH, NPA, SARFAESI
├── config/               # Desktop/docs configuration
├── consumer_finance/     # POS lending
├── credit_management/    # Credit scores, reports
├── customer_management/  # Customers, KYC, leads
├── dashboard_chart/      # Dashboard charts
├── education_loan/       # Education lending
├── fixtures/             # Roles, module defs, custom fields
├── foundation/           # Company, branch, products
├── gold_loan/            # Gold loan, vault, auction
├── home_loan/            # Home loan, PMAY, tranches
├── insurance/            # Insurance policies, claims
├── integrations/         # API integrations
├── investments/          # Mutual funds, FD, digital gold
├── invoice_finance/      # Invoice discounting
├── loans/                # Core loan management
├── microfinance/         # MFI/JLG/SHG lending
├── nbfc_lending/         # NBFC loan applications
├── number_card/          # Dashboard number cards
├── patches/              # Migration patches
├── payments/             # Bill payments, recharges
├── portfolio_management/ # Portfolio, goals
├── public/               # JS/CSS assets
├── risk_compliance/      # AML, fraud, regulatory reports
├── vehicle_loan/         # Vehicle loan, repossession
├── workspace/            # Workspace configuration
├── api.py                # REST API endpoints
├── hooks.py              # App hooks
├── permissions.py        # Permission query conditions
├── tasks.py              # Scheduled tasks
└── migrate_workspace.py  # Auto workspace sync
```

---

## 🔗 API Endpoints

The platform exposes REST APIs for all major operations:

- `GET /api/method/bizaxl_finance.api.get_customer_dashboard`
- `GET /api/method/bizaxl_finance.api.get_recent_transactions`
- `GET /api/method/bizaxl_finance.api.get_portfolio_summary`
- `GET /api/method/bizaxl_finance.api.get_loan_summary`
- `GET /api/method/bizaxl_finance.api.get_insurance_summary`
- `POST /api/method/bizaxl_finance.api.initiate_upi_transfer`
- `POST /api/method/bizaxl_finance.api.initiate_bill_payment`

---

## 🧪 Demo Data Loader

A comprehensive demo data loader is included to populate **70+ of the 106 DocTypes** with realistic Indian demo data. (Child tables, single DocTypes, and system-level DocTypes are excluded as they handle configuration or data entry.)

### Features
- **300+ records** across 22 modules
- Realistic names, addresses, PAN/Aadhaar numbers, and financial amounts
- All verticals covered: NBFC, MFI, Gold, Vehicle, Home, Personal, Business, Education, BNPL, Invoice, Chit, Consumer
- Safe to run multiple times (skips duplicates automatically)
- Shows progress with ✅/⚠️ indicators per module

### Usage

```bash
# Open site console
bench --site your-site.com console
```

Paste this single line inside the console:
```python
exec(open("../apps/bizaxl_finance/bizaxl_finance/load_demo_data.py").read())
```

Or run via bench execute:
```bash
bench --site your-site.com execute bizaxl_finance.load_demo_data.load_demo_data
```

Then clear cache and refresh:
```bash
bench --site your-site.com clear-cache
bench clear-cache
bench restart
```

### Sample Data Created

| Module | Records | Includes |
|--------|---------|----------|
| Foundation | 14 | 2 Company Configs, 6 Branches, 4 Rate Engines, 4 Charges |
| Customers | 18 | 6 Customers, 5 Leads, 2 DSAs, KYC Docs, Nominations |
| Banking | 25+ | Bank Accounts, UPI IDs, Transactions |
| Loans | 40+ | 6 Products, Applications, Disbursements, EMIs, Repayments |
| Insurance | 12 | 3 Products, Policies, Premiums |
| Investments | 20+ | Accounts, 5 Mutual Funds, FDs, Goals |
| Portfolio | 20+ | 6 Asset Classes, Holdings, Financial Goals |
| Gold Loan | 10+ | Pledges, Vault, Auctioneer |
| Vehicle | 12+ | Dealers, Vehicles, Repossessions |
| Home Loan | 15+ | Properties, Tranches, PMAY, Legal Opinions |
| Business Loan | 10+ | Profiles, Covenants |
| Education | 8+ | Institutions, Courses |
| BNPL | 12+ | Limits, Transactions |
| Invoice Finance | 8+ | Anchors, Invoices |
| Chit Fund | 15+ | Groups, Subscribers, Auctions |
| Consumer Finance | 10+ | Retailers, POS Transactions |
| Collections | 25+ | NACH, Records, NPA, SARFAESI |
| Risk & Compliance | 15+ | AML, Fraud Alerts, Reports |
| Accounting | 12+ | Provisioning, Funds, Co-lending |
| Credit Mgmt | 15+ | Reports, Scores, Goals |
| Microfinance | 20+ | Centers, JLG Groups, Members |
| NBFC | 3 | Loan Applications |

---

## 🛠️ Helper Scripts

### fix_integration_settings.py

Creates the `Integration Settings` Single DocType record in the database. Use this if the Integration Settings link in the workspace shows "Module Bizaxl Finance not found".

```bash
bench --site your-site.com console
```

```python
exec(open("../apps/bizaxl_finance/bizaxl_finance/fix_integration_settings.py").read())
```

Then:
```bash
bench --site your-site.com clear-cache
bench restart
```

### migrate_workspace.py

Force-syncs the workspace fixture to restore all 24 card sections with all links.

```bash
bench --site your-site.com console
```

```python
exec(open("../apps/bizaxl_finance/bizaxl_finance/migrate_workspace.py").read())
```

---

## 📄 License

MIT

---

## 👨‍💻 About

Built by **Bizaxl Technologies** — Accelerating Your Growth.

*Bizaxl Finance Platform v1.0 — Complete Financial Services for the Indian Market*
