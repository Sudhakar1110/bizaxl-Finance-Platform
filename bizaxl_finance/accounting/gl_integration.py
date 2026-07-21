"""Accounting & Treasury Integration Layer

Connects loan transactions to ERPNext's native Double-Entry Accounting.
Uses ERPNext Journal Entry for all GL postings (never writes GL Entry directly).

Transaction Mapping:
    Loan Disbursement  → Debit Loan Receivable / Credit Bank
    Loan Repayment     → Debit Bank / Credit Loan Receivable + Interest Income
    Interest Accrual   → Debit Interest Receivable / Credit Interest Income
    Provision          → Debit Provision Expense / Credit NPA Provision
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime, flt, add_days, add_months


def post_disbursement(loan, disbursement):
    """Post loan disbursement to GL via ERPNext Journal Entry
    
    Args:
        loan: Loan Application doc
        disbursement: Loan Disbursement doc
    
    Accounting:
        Dr. Loan Receivable (Asset)
        Cr. Bank Account (Asset)
    """
    settings = _get_accounting_settings()
    if not settings or not settings.auto_post_to_gl:
        return
    
    try:
        jv = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": disbursement.disbursement_date or today(),
            "company": settings.company,
            "user_remark": f"Loan Disbursement: {loan.name} - {disbursement.name}",
            "accounts": [
                {
                    "account": settings.loan_receivable_account,
                    "debit_in_account_currency": flt(disbursement.disbursed_amount or loan.loan_amount),
                    "reference_type": "Loan Application",
                    "reference_name": loan.name,
                },
                {
                    "account": settings.disbursement_bank_account,
                    "credit_in_account_currency": flt(disbursement.disbursed_amount or loan.loan_amount),
                    "reference_type": "Loan Application",
                    "reference_name": loan.name,
                },
            ],
        })
        jv.insert(ignore_permissions=True)
        jv.submit()
        
        # Link the Journal Entry back to the disbursement
        frappe.db.set_value("Loan Disbursement", disbursement.name, "gl_entry_reference", jv.name)
        return jv.name
    except Exception as e:
        frappe.log_error(f"GL posting failed for disbursement {disbursement.name}: {e}", "Accounting")


def post_repayment(repayment):
    """Post loan repayment to GL via ERPNext Journal Entry
    
    Args:
        repayment: Loan Repayment doc
    
    Accounting:
        Dr. Bank Account (Asset)
            Cr. Loan Receivable (Asset) — Principal portion
            Cr. Interest Income (Income) — Interest portion
    """
    settings = _get_accounting_settings()
    if not settings or not settings.auto_post_to_gl:
        return
    
    try:
        principal = flt(repayment.principal_amount or repayment.amount * 0.8)
        interest = flt(repayment.interest_amount or repayment.amount * 0.2)
        
        txn_date = repayment.repayment_date or today()
        if hasattr(repayment, 'payment_date') and repayment.payment_date:
            txn_date = repayment.payment_date
        
        jv = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": txn_date,
            "company": settings.company,
            "user_remark": f"Loan Repayment: {repayment.loan_application} - {repayment.name}",
            "accounts": [
                {
                    "account": settings.repayment_bank_account or settings.disbursement_bank_account,
                    "debit_in_account_currency": flt(repayment.amount),
                    "reference_type": "Loan Application",
                    "reference_name": repayment.loan_application,
                },
                {
                    "account": settings.loan_receivable_account,
                    "credit_in_account_currency": principal,
                    "reference_type": "Loan Application",
                    "reference_name": repayment.loan_application,
                },
                {
                    "account": settings.interest_income_account,
                    "credit_in_account_currency": interest,
                    "reference_type": "Loan Application",
                    "reference_name": repayment.loan_application,
                },
            ],
        })
        jv.insert(ignore_permissions=True)
        jv.submit()
        
        frappe.db.set_value("Loan Repayment", repayment.name, "gl_entry_reference", jv.name)
        return jv.name
    except Exception as e:
        frappe.log_error(f"GL posting failed for repayment {repayment.name}: {e}", "Accounting")


def accrue_interest():
    """Monthly: Accrue interest on all active loans
    
    Creates a single summary Journal Entry for the period's interest.
    Called by scheduled task.
    """
    settings = _get_accounting_settings()
    if not settings or not settings.auto_accrue_interest:
        return
    
    period_start = add_months(today(), -1)
    period_end = today()
    
    # Get all active loans with accrued interest
    loans = frappe.db.sql("""
        SELECT la.name, la.customer, la.loan_amount, la.interest_rate,
               COALESCE(SUM(lr.amount), 0) as total_repaid
        FROM `tabLoan Application` la
        LEFT JOIN `tabLoan Repayment` lr ON lr.loan_application = la.name
        WHERE la.status = 'Disbursed'
        GROUP BY la.name
        HAVING la.loan_amount > total_repaid AND la.loan_amount > 0
    """, as_dict=True)
    
    if not loans:
        return
    
    total_interest = 0
    accounts_data = []
    
    for loan in loans:
        monthly_interest = flt(loan.loan_amount * (loan.interest_rate / 100 / 12))
        if monthly_interest <= 0:
            continue
        total_interest += monthly_interest
        accounts_data.append({
            "account": settings.interest_receivable_account,
            "debit_in_account_currency": monthly_interest,
            "reference_type": "Loan Application",
            "reference_name": loan.name,
        })
        accounts_data.append({
            "account": settings.interest_income_account,
            "credit_in_account_currency": monthly_interest,
            "reference_type": "Loan Application",
            "reference_name": loan.name,
        })
    
    if total_interest <= 0:
        return
    
    try:
        jv = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": period_end,
            "company": settings.company,
            "user_remark": f"Monthly Interest Accrual: {period_start} to {period_end}",
            "accounts": accounts_data,
        })
        jv.insert(ignore_permissions=True)
        jv.submit()
        frappe.log_error(f"Interest accrual JE created: {jv.name} for ₹{total_interest:,.2f}", "Accounting")
    except Exception as e:
        frappe.log_error(f"Interest accrual posting failed: {e}", "Accounting")


def create_provision(npa_classification):
    """Create NPA provision entry based on NPA classification
    
    Accounting:
        Dr. Provision Expense (Expense)
        Cr. NPA Provision Reserve (Liability)
    """
    settings = _get_accounting_settings()
    if not settings or not settings.auto_post_provision:
        return
    
    try:
        provision_amount = flt(npa_classification.provision_amount or 
                               npa_classification.outstanding_amount * 0.15)
        
        jv = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": today(),
            "company": settings.company,
            "user_remark": f"NPA Provision: {npa_classification.loan_account} - {npa_classification.npa_category}",
            "accounts": [
                {
                    "account": settings.provision_expense_account,
                    "debit_in_account_currency": provision_amount,
                },
                {
                    "account": settings.npa_provision_account,
                    "credit_in_account_currency": provision_amount,
                },
            ],
        })
        jv.insert(ignore_permissions=True)
        jv.submit()
        frappe.db.set_value("NPA Classification", npa_classification.name, 
                           "provision_jv_reference", jv.name)
        return jv.name
    except Exception as e:
        frappe.log_error(f"Provision posting failed: {e}", "Accounting")


def _get_accounting_settings():
    """Get active GL Settings configuration"""
    try:
        settings = frappe.get_single_doc("GL Settings")
        if not settings.company or not settings.loan_receivable_account:
            frappe.log_error(
                "GL Settings not fully configured — set Company and Loan Receivable Account",
                "Accounting"
            )
            return None
        return settings
    except Exception as e:
        frappe.log_error(f"Failed to load GL Settings: {e}", "Accounting")
        return None


# ── Co-Lending P&L Split ────────────────────────────────────────────────

def calculate_colending_split(loan, partner_share=0.80):
    """Calculate co-lending P&L split between lead and partner"""
    return {
        "lead_share": flt(loan.loan_amount * (1 - partner_share)),
        "partner_share": flt(loan.loan_amount * partner_share),
        "lead_interest_pct": flt(loan.interest_rate),
        "partner_interest_pct": flt(loan.interest_rate * 0.9),
    }


def post_securitization(loan_pool, purchaser, price):
    """Post securitization transaction — sell loan pool to purchaser"""
    settings = _get_accounting_settings()
    if not settings:
        return
    
    try:
        jv = frappe.get_doc({
            "doctype": "Journal Entry",
            "voucher_type": "Journal Entry",
            "posting_date": today(),
            "company": settings.company,
            "user_remark": f"Securitization: Pool sold to {purchaser}",
            "accounts": [
                {
                    "account": settings.disbursement_bank_account,
                    "debit_in_account_currency": flt(price),
                },
                {
                    "account": settings.loan_receivable_account,
                    "credit_in_account_currency": flt(price),
                },
            ],
        })
        jv.insert(ignore_permissions=True)
        jv.submit()
        return jv.name
    except Exception as e:
        frappe.log_error(f"Securitization posting failed: {e}", "Accounting")
