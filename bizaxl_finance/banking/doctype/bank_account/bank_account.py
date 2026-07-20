from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime

class BankAccount(Document):
    def validate(self):
        self.validate_ifsc()
        self.validate_account_number()
        self.set_customer_primary_account()

    def before_save(self):
        self.available_balance = self.current_balance

    def validate_ifsc(self):
        if self.ifsc_code:
            ifsc = self.ifsc_code.upper()
            if not (len(ifsc) == 11 and ifsc[:4].isalpha() and ifsc[4] == '0' and ifsc[5:].isalnum()):
                frappe.throw("Invalid IFSC Code. It should be 11 characters (e.g., SBIN0123456)")

    def validate_account_number(self):
        if self.account_number:
            # Basic validation - at least 9 digits for meaningful account numbers
            if len(self.account_number) < 9 or len(self.account_number) > 18:
                frappe.throw("Account number should be between 9 and 18 digits")

    def set_customer_primary_account(self):
        """Set as primary account if checked and update customer"""
        if self.is_primary:
            frappe.db.sql("""
                UPDATE `tabBank Account`
                SET is_primary = 0
                WHERE customer = %s AND name != %s
            """, (self.customer, self.name or "New"))

            # Update customer's primary bank account
            frappe.db.set_value("Bizaxl Customer", self.customer,
                "primary_bank_account", self.account_number)

    def get_balance(self):
        return self.current_balance

    def update_balance(self, amount, transaction_type):
        """Update balance after a transaction"""
        if transaction_type in ["Credit", "Deposit", "Refund", "Interest"]:
            self.db_set("current_balance", self.current_balance + amount)
            self.db_set("available_balance", self.available_balance + amount)
            self.db_set("last_transaction_date", today())
        elif transaction_type in ["Debit", "Withdrawal", "Payment", "Transfer"]:
            if self.current_balance + (self.overdraft_limit or 0) >= amount:
                self.db_set("current_balance", self.current_balance - amount)
                self.db_set("available_balance", self.available_balance - amount)
                self.db_set("last_transaction_date", today())
            else:
                frappe.throw("Insufficient balance in account " + self.account_number)
