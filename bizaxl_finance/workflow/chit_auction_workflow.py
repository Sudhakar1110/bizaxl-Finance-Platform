"""Chit Fund Auction Workflow

Auction lifecycle:
    Scheduled → Bidding Open → Bid Awarded → Prize Disbursed → Completed
                                    ↓
                                No Bidder → Rescheduled
"""

import frappe


def create_chit_auction_workflow():
    """Create the chit auction workflow"""
    if frappe.db.exists("Workflow", "Chit Auction Processing"):
        return "Workflow already exists"
    
    workflow = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": "Chit Auction Processing",
        "document_type": "Chit Auction",
        "is_active": 1,
        "workflow_state_field": "workflow_state",
        
        "states": [
            {"state": "Scheduled", "doc_status": 0, "allow_edit": "Chit Foreman"},
            {"state": "Bidding Open", "doc_status": 0, "allow_edit": "Chit Foreman"},
            {"state": "Bid Awarded", "doc_status": 1, "allow_edit": "Chit Foreman"},
            {"state": "Prize Disbursed", "doc_status": 1, "allow_edit": "Branch Manager"},
            {"state": "Completed", "doc_status": 1, "allow_edit": "Branch Manager"},
            {"state": "Rescheduled", "doc_status": 1, "allow_edit": "Chit Foreman"},
        ],
        
        "transitions": [
            {"state": "Scheduled", "action": "Open Bidding", "next_state": "Bidding Open", "allowed": "Chit Foreman"},
            {"state": "Bidding Open", "action": "Award to Winner", "next_state": "Bid Awarded", "allowed": "Chit Foreman"},
            {"state": "Bidding Open", "action": "No Bidders", "next_state": "Rescheduled", "allowed": "Chit Foreman"},
            {"state": "Bid Awarded", "action": "Disburse Prize", "next_state": "Prize Disbursed", "allowed": "Branch Manager"},
            {"state": "Prize Disbursed", "action": "Complete Auction", "next_state": "Completed", "allowed": "Branch Manager"},
            {"state": "Rescheduled", "action": "Schedule New Date", "next_state": "Scheduled", "allowed": "Chit Foreman"},
        ],
    })
    
    workflow.insert(ignore_permissions=True)
    frappe.db.commit()
    return f"Workflow '{workflow.name}' created"
