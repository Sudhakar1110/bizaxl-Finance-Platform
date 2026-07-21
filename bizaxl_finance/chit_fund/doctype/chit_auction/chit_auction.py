import json
import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class ChitAuction(Document):
    def validate(self):
        self.calculate_prize_and_commission()
        self.calculate_dividend()

    def calculate_prize_and_commission(self):
        """Calculate prize amount and foreman commission"""
        if self.chit_group and self.bid_amount:
            chit_group = frappe.get_cached_doc("Chit Group", self.chit_group)
            chit_value = flt(chit_group.chit_value or 0)
            foreman_commission_pct = flt(chit_group.foreman_commission or 5) / 100

            # Prize = Chit Value - Winning Bid
            self.prize_amount = chit_value - flt(self.bid_amount)

            # Foreman Commission = Chit Value * Commission %
            self.foreman_commission = chit_value * foreman_commission_pct

    def calculate_dividend(self):
        """
        Calculate dividend for non-prized subscribers.

        Dividend Calculation:
        1. Amount available for distribution = Winning Bid Amount - Foreman Commission
        2. Dividend per non-prized member = Available Amount / Number of non-prized subscribers

        The dividend is credited to each non-prized subscriber's chit account
        as a reduction in their future subscription.
        """
        if not self.chit_group or not self.bid_amount or not self.foreman_commission:
            return

        chit_group = frappe.get_cached_doc("Chit Group", self.chit_group)
        if not chit_group:
            return

        total_members = flt(chit_group.number_of_members or 1)

        # Find how many auctions have been conducted (including this one)
        conducted_auctions = frappe.db.count("Chit Auction", {
            "chit_group": self.chit_group,
            "status": ["in", ["Conducted", "Completed"]]
        })

        # Non-prized = Won't include this auction's winner
        # For each auction, exactly 1 member becomes prized
        non_prized_count = int(total_members - max(conducted_auctions, 1))
        self.non_prized_count = max(non_prized_count, 0)

        if non_prized_count <= 0:
            return

        # Amount available for dividend = Bid Amount - Foreman Commission
        available_for_dividend = flt(self.bid_amount) - flt(self.foreman_commission)

        if available_for_dividend <= 0:
            return

        # Dividend per non-prized member
        dividend_per_member = available_for_dividend / non_prized_count
        self.dividend_per_member = round(dividend_per_member, 2)
        self.total_dividend_amount = round(dividend_per_member * non_prized_count, 2)

        # Generate dividend summary JSON for audit trail
        self.dividend_summary_json = json.dumps({
            "auction_number": self.auction_number,
            "chit_group": self.chit_group,
            "chit_value": flt(chit_group.chit_value),
            "bid_amount": flt(self.bid_amount),
            "prize_amount": flt(self.prize_amount),
            "foreman_commission": flt(self.foreman_commission),
            "available_for_dividend": flt(available_for_dividend),
            "non_prized_count": non_prized_count,
            "dividend_per_member": round(dividend_per_member, 2),
            "total_dividend_amount": round(dividend_per_member * non_prized_count, 2),
            "calculated_on": str(today()),
        }, indent=2)

    def mark_dividend_paid(self):
        """Mark dividend as paid to non-prized subscribers"""
        self.dividend_paid = 1
        self.dividend_distribution_date = today()
        frappe.msgprint(
            f"✅ Dividend of ₹{self.dividend_per_member:,.2f} paid to "
            f"{self.non_prized_count} non-prized members",
            alert=True, indicator="green"
        )

    def get_dividend_summary(self):
        """Return human-readable dividend summary"""
        if not self.dividend_summary_json:
            return "Dividend not calculated yet"

        summary = json.loads(self.dividend_summary_json)
        return (
            f"Auction #{summary['auction_number']}:\n"
            f"  Chit Value: ₹{summary['chit_value']:,.2f}\n"
            f"  Bid Amount: ₹{summary['bid_amount']:,.2f}\n"
            f"  Prize: ₹{summary['prize_amount']:,.2f}\n"
            f"  Commission: ₹{summary['foreman_commission']:,.2f}\n"
            f"  Dividend/Non-prized: ₹{summary['dividend_per_member']:,.2f} "
            f"× {summary['non_prized_count']} members\n"
            f"  Total Dividend: ₹{summary['total_dividend_amount']:,.2f}"
        )
