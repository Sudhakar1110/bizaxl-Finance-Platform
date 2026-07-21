"""Loan Application Workflow — BPM Approval Process

Configures a Frappe Workflow on the Loan Application DocType:
    Draft → Under Review → Approved → Disbursed → Closed
                    ↓                      
                 Rejected

Tiered Approval:
    - Rs.0-5L: Branch Manager approval
    - Rs.5L-25L: Credit Committee approval
    - Rs.25L+: Board-level approval

Integrates with ERPNext v15 Workflow engine.
"""

import frappe
from frappe import _


def create_loan_application_workflow():
    """Create the Loan Application approval workflow programmatically.
    
    Call this in a patch or after_install hook.
    """
    if frappe.db.exists("Workflow", "Loan Application Approval"):
        return "Workflow already exists"
    
    workflow = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": "Loan Application Approval",
        "document_type": "Loan Application",
        "is_active": 1,
        "override_status": 0,
        "send_email_alert": 1,
        "workflow_state_field": "workflow_state",
        
        "states": [
            {
                "state": "Draft",
                "doc_status": 0,
                "allow_edit": "System Admin",
                "update_field": "status",
                "update_value": "Draft",
            },
            {
                "state": "Under Review",
                "doc_status": 0,
                "allow_edit": "Credit Officer",
                "update_field": "status",
                "update_value": "Under Review",
            },
            {
                "state": "Credit Committee",
                "doc_status": 0,
                "allow_edit": "Credit Officer",
                "update_field": "status",
                "update_value": "Under Review",
            },
            {
                "state": "Approved",
                "doc_status": 1,
                "allow_edit": "Loan Manager",
                "update_field": "status",
                "update_value": "Approved",
            },
            {
                "state": "Disbursed",
                "doc_status": 1,
                "allow_edit": "Loan Manager",
                "update_field": "status",
                "update_value": "Disbursed",
            },
            {
                "state": "Rejected",
                "doc_status": 1,
                "allow_edit": "Credit Officer",
                "update_field": "status",
                "update_value": "Rejected",
            },
            {
                "state": "Closed",
                "doc_status": 1,
                "allow_edit": "Loan Manager",
                "update_field": "status",
                "update_value": "Closed",
            },
        ],
        
        "transitions": [
            {
                "state": "Draft",
                "action": "Submit for Review",
                "next_state": "Under Review",
                "allowed": "Customer",
                "condition": "doc.loan_amount > 0",
            },
            {
                "state": "Under Review",
                "action": "Credit Assessment",
                "next_state": "Credit Committee",
                "allowed": "Credit Officer",
                "condition": "doc.loan_amount <= 2500000",
            },
            {
                "state": "Under Review",
                "action": "Send to Board",
                "next_state": "Credit Committee",
                "allowed": "Credit Officer",
                "condition": "doc.loan_amount > 2500000",
            },
            {
                "state": "Credit Committee",
                "action": "Approve",
                "next_state": "Approved",
                "allowed": "Branch Manager",
                "condition": "doc.loan_amount <= 500000",
            },
            {
                "state": "Credit Committee",
                "action": "Approve",
                "next_state": "Approved",
                "allowed": "Loan Manager",
                "condition": "doc.loan_amount > 500000 AND doc.loan_amount <= 2500000",
            },
            {
                "state": "Credit Committee",
                "action": "Approve",
                "next_state": "Approved",
                "allowed": "System Admin",
                "condition": "doc.loan_amount > 2500000",
            },
            {
                "state": "Credit Committee",
                "action": "Reject",
                "next_state": "Rejected",
                "allowed": "Credit Officer",
            },
            {
                "state": "Approved",
                "action": "Disburse",
                "next_state": "Disbursed",
                "allowed": "Loan Manager",
                "condition": "doc.disbursement_date IS NOT NULL",
            },
            {
                "state": "Disbursed",
                "action": "Close Loan",
                "next_state": "Closed",
                "allowed": "Loan Manager",
                "condition": "doc.status = 'Closed'",
            },
        ],
    })
    
    workflow.insert(ignore_permissions=True)
    frappe.db.commit()
    return f"Workflow '{workflow.name}' created successfully"


def create_kyc_verification_workflow():
    """Create KYC Document verification workflow"""
    if frappe.db.exists("Workflow", "KYC Document Verification"):
        return "Workflow already exists"
    
    workflow = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": "KYC Document Verification",
        "document_type": "KYC Document",
        "is_active": 1,
        "workflow_state_field": "workflow_state",
        
        "states": [
            {"state": "Pending", "doc_status": 0, "allow_edit": "Customer"},
            {"state": "Under Review", "doc_status": 0, "allow_edit": "Compliance Officer"},
            {"state": "Verified", "doc_status": 1, "allow_edit": "Customer Service Representative"},
            {"state": "Rejected", "doc_status": 1, "allow_edit": "Compliance Officer"},
        ],
        
        "transitions": [
            {"state": "Pending", "action": "Submit for Verification", "next_state": "Under Review", "allowed": "Customer"},
            {"state": "Under Review", "action": "Approve", "next_state": "Verified", "allowed": "Compliance Officer"},
            {"state": "Under Review", "action": "Reject", "next_state": "Rejected", "allowed": "Compliance Officer"},
            {"state": "Rejected", "action": "Re-submit", "next_state": "Pending", "allowed": "Customer"},
        ],
    })
    
    workflow.insert(ignore_permissions=True)
    frappe.db.commit()
    return f"Workflow '{workflow.name}' created"
