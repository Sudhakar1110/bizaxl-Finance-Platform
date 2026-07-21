import frappe
from frappe.model.document import Document
from frappe.utils import today, flt


class VehicleRepossession(Document):
    def validate(self):
        self.set_yard_in_date()
        self.update_vehicle_status()
        self.calculate_net_recovery()

    def before_submit(self):
        if not self.status or self.status == "Repossessed":
            self.status = "In Yard"

    def set_yard_in_date(self):
        """Set yard in date when vehicle enters storage"""
        if self.status == "In Yard" and not self.yard_in_date:
            self.yard_in_date = today()

    def update_vehicle_status(self):
        """Update linked Vehicle Detail status on repossession"""
        if self.vehicle:
            frappe.db.set_value("Vehicle Detail", self.vehicle, "status", "Repossessed")

    def calculate_net_recovery(self):
        """Calculate net recovery after auction"""
        if self.auction_amount and self.estimated_value:
            recovery_rate = (self.auction_amount / self.estimated_value) * 100
            # Store in remarks
            note = f"Recovery: {recovery_rate:.1f}% of estimated value"
            if self.remarks:
                if note not in self.remarks:
                    self.remarks += f"\n{note}"
            else:
                self.remarks = note

            # Add yard charges to recovery cost
            total_cost = flt(self.recovery_cost or 0) + flt(self.yard_charges or 0)
            net_recovery = flt(self.auction_amount) - total_cost
            note2 = f"Net Recovery: ₹{net_recovery:,.2f} (after costs: ₹{total_cost:,.2f})"
            if note2 not in self.remarks:
                self.remarks += f"\n{note2}"

    def release_from_yard(self):
        """Release vehicle from yard (after auction/return)"""
        self.yard_release_date = today()
        self.status = "Auctioned"
        frappe.msgprint(
            f"Vehicle released from yard on {today()}",
            alert=True, indicator="green"
        )
