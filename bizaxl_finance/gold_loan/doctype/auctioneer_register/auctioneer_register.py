import frappe
from frappe.model.document import Document
from frappe.utils import today


class AuctioneerRegister(Document):
    def validate(self):
        self.set_defaults()
        self.validate_empanelement()

    def set_defaults(self):
        if not self.empanelement_date:
            self.empanelement_date = today()

    def validate_empanelement(self):
        """Validate auctioneer empanelement"""
        if self.valid_until and self.valid_until < today():
            self.status = "Expired"
            frappe.msgprint(
                f"Empanelement expired on {self.valid_until}. Status set to Expired.",
                alert=True, indicator="orange"
            )

    def update_performance_stats(self, auction_amount, recovery_rate):
        """Update auctioneer performance after an auction"""
        self.total_auctions_conducted = (self.total_auctions_conducted or 0) + 1
        self.total_value_auctioned = (self.total_value_auctioned or 0) + auction_amount
        self.last_auction_date = today()

        if self.total_auctions_conducted > 0:
            # Calculate average recovery rate
            current_total = (self.total_value_auctioned or 0)
            self.average_recovery_rate = round(
                (recovery_rate + (self.average_recovery_rate or 0) * (self.total_auctions_conducted - 1))
                / self.total_auctions_conducted, 2
            )

        frappe.msgprint(
            f"Performance updated for {self.auctioneer_name}",
            alert=True, indicator="green"
        )
