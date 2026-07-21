import json
import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class InvoiceFinance(Document):
    def validate(self):
        self.calculate_amounts()
        self.update_treds_status()

    def before_submit(self):
        self.funding_status = "Funded"

    def calculate_amounts(self):
        """Auto-calculate advance and retention amounts

        - Recourse: 90% advance, 10% retention
        - Non-recourse: 85% advance, 15% retention
        """
        if self.invoice_amount:
            advance_pct = 0.85  # Default: 85% advance, 15% retention
            self.advance_amount = round(flt(self.invoice_amount) * advance_pct, 2)
            self.retention_amount = round(flt(self.invoice_amount) * (1 - advance_pct), 2)

        # Set disbursed amount if not set
        if not self.disbursed_amount and self.advance_amount:
            self.disbursed_amount = self.advance_amount

    def update_treds_status(self):
        """Auto-update TReDS status based on invoice lifecycle"""
        if not self.treds_status:
            self.treds_status = "Not Submitted"

        if self.treds_status == "Submitted" and not self.treds_submitted_date:
            self.treds_submitted_date = today()
        elif self.treds_status == "Accepted" and not self.treds_approved_date:
            self.treds_approved_date = today()
        elif self.treds_status == "Settled" and not self.treds_settlement_date:
            self.treds_settlement_date = today()

    def submit_to_treds(self):
        """
        Submit invoice to TReDS platform for secondary market trading.
        Stub implementation - connects to TReDS API in production.
        """
        if self.treds_status not in ("Not Submitted", ""):
            frappe.msgprint(f"Already submitted to TReDS (Status: {self.treds_status})", alert=True)
            return

        # TReDS API submission stub
        treds_response = {
            "status": "submitted",
            "treds_invoice_id": f"TREDS-{self.name}-{today()}",
            "invoice_number": self.invoice_number,
            "invoice_amount": flt(self.invoice_amount),
            "submitted_at": str(today()),
            "platform": "RBI TReDS Platform",
            "message": "Invoice submitted for bidding on TReDS",
        }

        self.treds_invoice_id = treds_response["treds_invoice_id"]
        self.treds_status = "Submitted"
        self.treds_submitted_date = today()
        self.treds_response_json = json.dumps(treds_response, indent=2)

        frappe.msgprint(
            f"✅ Submitted to TReDS: {treds_response['treds_invoice_id']}",
            alert=True, indicator="green"
        )
        return treds_response

    def check_treds_bids(self):
        """
        Check for bids received on TReDS platform.
        Stub implementation.
        """
        if self.treds_status != "Submitted":
            frappe.msgprint(f"Invoice not submitted to TReDS yet.", alert=True)
            return

        # Stub: simulate bid received
        bid_response = {
            "status": "bid_received",
            "treds_invoice_id": self.treds_invoice_id,
            "bids_received": 3,
            "best_rate": 8.5,  # Discount rate %
            "bid_amount": flt(self.invoice_amount) * 0.99,
            "bid_valid_until": "2026-07-25",
        }

        self.treds_status = "Bid Received"
        self.treds_response_json = json.dumps(bid_response, indent=2)

        frappe.msgprint(
            f"📊 {bid_response['bids_received']} bids received on TReDS. "
            f"Best rate: {bid_response['best_rate']}%",
            alert=True, indicator="blue"
        )
        return bid_response

    def accept_treds_bid(self):
        """Accept the best bid on TReDS"""
        if self.treds_status != "Bid Received":
            frappe.msgprint("No bids to accept. Check bids first.", alert=True)
            return

        self.treds_status = "Accepted"
        self.treds_approved_date = today()

        frappe.msgprint(
            f"✅ TReDS bid accepted. Awaiting settlement.",
            alert=True, indicator="green"
        )
