"""e-Sign Document Generator

Generates loan documents as PDF print formats and initiates the e-Sign workflow.
Integrates with:
    1. Frappe Print Format engine (PDF generation)
    2. e-Sign connector (Aadhaar OTP-based signing)
    3. Customer Communication (notification)

Workflow:
    Create Document → Generate PDF → Initiate e-Sign → Store Signed Copy → Notify
"""

import frappe
from frappe import _
from frappe.utils import today, now_datetime
import json


def generate_loan_agreement(loan_application):
    """Generate Loan Agreement PDF and return the file path
    
    Args:
        loan_application: Loan Application doc name
        
    Returns:
        dict with file URL and status
    """
    try:
        # Use Frappe Print Format engine to generate PDF
        pdf_data = frappe.get_print(
            doctype="Loan Application",
            name=loan_application,
            print_format="Loan Agreement",
            as_pdf=True,
            output=None,
        )
        
        # Save as file attachment
        from frappe.utils.file_manager import save_file
        
        filename = f"Loan_Agreement_{loan_application}_{today()}.pdf"
        file_doc = save_file(
            fname=filename,
            content=pdf_data,
            dt="Loan Application",
            dn=loan_application,
            folder="Home/Attachments",
            is_private=1,
        )
        
        return {
            "success": True,
            "file_url": file_doc.file_url,
            "file_name": filename,
            "message": "Loan Agreement PDF generated",
        }
    except Exception as e:
        frappe.log_error(f"Loan agreement generation failed: {e}", "e-Sign")
        return {"error": str(e), "file_url": None}


def generate_sanction_letter(loan_application):
    """Generate Sanction Letter PDF"""
    try:
        pdf_data = frappe.get_print(
            doctype="Loan Application",
            name=loan_application,
            print_format="Sanction Letter",
            as_pdf=True,
        )
        
        from frappe.utils.file_manager import save_file
        
        filename = f"Sanction_Letter_{loan_application}_{today()}.pdf"
        file_doc = save_file(
            fname=filename,
            content=pdf_data,
            dt="Loan Application",
            dn=loan_application,
            folder="Home/Attachments",
            is_private=1,
        )
        
        return {"success": True, "file_url": file_doc.file_url, "file_name": filename}
    except Exception as e:
        frappe.log_error(f"Sanction letter generation failed: {e}", "e-Sign")
        return {"error": str(e)}


def initiate_esign(document_id, file_url, aadhaar_number, customer):
    """Initiate e-Sign process via the integration connector
    
    Args:
        document_id: Loan Application or doc name
        file_url: URL of the generated PDF
        aadhaar_number: Customer's Aadhaar for OTP
        customer: Customer name (Bizaxl Customer)
        
    Returns:
        dict with signing reference and status
    """
    from bizaxl_finance.integrations.esign import request_esign
    
    result = request_esign(
        document_id=document_id,
        aadhaar_number=aadhaar_number,
        callback_url=f"/api/method/bizaxl_finance.esign.document_generator.esign_callback",
    )
    
    if result.get("success"):
        # Notify customer
        customer_name = frappe.db.get_value("Bizaxl Customer", customer, "customer_name")
        frappe.get_doc({
            "doctype": "Customer Communication",
            "customer": customer,
            "subject": "Document Ready for e-Sign",
            "message_body": f"Your loan document is ready for e-signing. "
                           f"Please check your Aadhaar-linked mobile for OTP.",
            "channel": "App Notification",
            "communication_type": "Notification",
            "status": "Sent",
        }).insert(ignore_permissions=True)
    
    return result


def esign_callback(**kwargs):
    """Callback after e-Sign is completed
    
    Updates the loan document with signed copy URL.
    """
    signing_ref = kwargs.get("signing_ref")
    document_id = kwargs.get("document_id")
    status = kwargs.get("status", "Signed")
    
    if not signing_ref or not document_id:
        return {"error": "Missing parameters"}
    
    # Update loan application with e-sign status
    frappe.db.set_value("Loan Application", document_id, {
        "esign_status": status,
        "esign_reference": signing_ref,
        "esign_date": today(),
    })
    
    frappe.db.commit()
    return {"success": True, "message": "e-Sign callback processed"}


def get_document_url(loan_application, doc_type="Loan Agreement"):
    """Get the document URL for display/download"""
    from frappe.utils.file_manager import get_file_url
    
    file_name = frappe.db.get_value("File", {
        "attached_to_doctype": "Loan Application",
        "attached_to_name": loan_application,
        "file_name": ["like", f"%{doc_type}%"],
    }, "file_url")
    
    return file_name or None


@frappe.whitelist()
def download_document(loan_application, doc_type="Loan Agreement"):
    """Download a signed loan document"""
    file_url = get_document_url(loan_application, doc_type)
    if file_url:
        return {"file_url": file_url}
    return {"error": "Document not found"}
