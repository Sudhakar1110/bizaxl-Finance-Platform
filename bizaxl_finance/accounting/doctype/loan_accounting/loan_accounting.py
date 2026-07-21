import frappe
from frappe.model.document import Document


class LoanAccounting(Document):
    """Tracks GL posting reference for each loan transaction.
    
    Links loan transactions (disbursements, repayments, accruals)
    to their corresponding ERPNext Journal Entry for audit trail.
    """
    pass
