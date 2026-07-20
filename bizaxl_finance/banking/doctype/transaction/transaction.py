from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
import uuid

class Transaction(Document):
    def validate(self):
        self.set_reference_number()
        self.validate_amount()
        self.set_balance()

    def before_submit(self):
        self.status = "Completed"
        self.update_account_balances()

    def before_cancel(self):
        self.status = "Cancelled"
        self.reverse_account_balances()

    def set_reference_number(self):
        if not self.reference_number:
            self.reference_number = "TXN" + str(uuid.uuid4()).replace("-", "").upper()[:12]

    def validate_amount(self):
        if self.amount <= 0:
            frappe.throw("Transaction amount must be greater than zero")

    def set_balance(self):
        """Set balance before transaction"""
        if self.from_account:
            account = frappe.get_doc("Bank Account", self.from_account)
            self.balance_before_transaction = account.current_balance
            if self.transaction_type in ["Debit", "Payment", "Transfer"]:
                self.balance_after_transaction = account.current_balance - self.amount
            else:
                self.balance_after_transaction = account.current_balance + self.amount

    def update_account_balances(self):
        """Update bank account balances on transaction submission"""
        if self.from_account:
            account = frappe.get_doc("Bank Account", self.from_account)
            account.update_balance(self.amount, self.transaction_type if self.transaction_type in ["Debit", "Payment", "Transfer"] else "Credit")

        if self.to_account and self.transaction_type == "Transfer":
            to_account = frappe.get_doc("Bank Account", self.to_account)
            to_account.update_balance(self.amount, "Credit")

        # Update customer's last transaction date
        frappe.db.set_value("Bizaxl Customer", self.customer, "last_transaction_date", now_datetime())

    def reverse_account_balances(self):
        """Reverse account balances on cancellation"""
        if not self.from_account:
            return
        account = frappe.get_doc("Bank Account", self.from_account)
        if self.transaction_type in ["Debit", "Payment", "Transfer"]:
            account.update_balance(self.amount, "Refund")
        elif account and account.current_balance:
            new_balance = max(0, account.current_balance - self.amount)
            account.db_set("current_balance", new_balance)

    def get_transaction_summary(self):
        """Returns summary for customer portal"""
        return {
            "reference_number": self.reference_number,
            "type": self.transaction_type,
            "amount": self.amount,
            "date": self.transaction_date,
            "description": self.description,
            "status": self.status,
            "from_account": self.from_account,
            "to_account": self.to_account,
        }
