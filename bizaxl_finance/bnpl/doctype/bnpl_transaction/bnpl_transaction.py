import math
import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class BNPLTransaction(Document):
    def validate(self):
        self.calculate_emi()
        self.calculate_subvention()

    def calculate_emi(self):
        """Calculate EMI for the BNPL transaction"""
        if self.transaction_amount and self.tenor_months:
            if self.tenor_months > 0:
                self.emi_amount = round(flt(self.transaction_amount) / self.tenor_months, 2)

    def calculate_subvention(self):
        """
        Calculate merchant subvention for 0% EMI offers.

        In a 0% EMI BNPL model:
        - Customer pays 0% interest
        - Merchant pays subvention to the platform
        - Subvention = interest that would have been charged at standard rate
        - Settlement to merchant = Transaction Amount - Subvention

        Formula:
        Subvention = Principal * Rate * Tenure / 12 / 100
        Settlement Amount = Transaction Amount - Subvention
        """
        if not self.transaction_amount or not self.tenor_months:
            return

        principal = flt(self.transaction_amount)
        tenure = flt(self.tenor_months)

        # Standard interest rate for BNPL (configurable per merchant type)
        standard_rates = {
            "Online": 24.0,
            "POS": 18.0,
            "E-commerce": 22.0,
            "Retail": 20.0,
            "Other": 18.0,
        }

        annual_rate = flt(self.subvention_rate or standard_rates.get(self.merchant_type, 20.0))

        if self.subvention_rate <= 0:
            self.subvention_rate = annual_rate

        # Calculate subvention using simple interest
        # Subvention = Principal * Rate * Time / 12 / 100
        subvention = principal * flt(self.subvention_rate) * tenure / 12 / 100
        self.subvention_amount = round(subvention, 2)

        # Settlement amount = Transaction Amount - Subvention
        self.merchant_settlement_amount = round(principal - subvention, 2)

        # Auto-update subvention status
        if self.subvention_amount > 0:
            self.subvention_status = "Calculated"

        # Set settlement date for D+2 settlement
        if self.transaction_date and not self.settlement_date:
            from frappe.utils import add_days
            self.settlement_date = add_days(self.transaction_date, 2)

    def mark_as_settled(self, reference=None):
        """Mark subvention as settled to merchant"""
        self.subvention_status = "Settled"
        self.settlement_reference = reference or f"SET-{self.name}-{today()}"
        self.settlement_date = today()
        frappe.msgprint(
            f"✅ Subvention settled: ₹{self.subvention_amount:,.2f}",
            alert=True, indicator="green"
        )
