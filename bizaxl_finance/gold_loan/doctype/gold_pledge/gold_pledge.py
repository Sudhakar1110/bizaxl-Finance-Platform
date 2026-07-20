import frappe
from frappe.model.document import Document


class GoldPledge(Document):
    def validate(self):
        if self.disbursement_date and self.tenure_months:
            self.maturity_date = frappe.utils.add_months(self.disbursement_date, self.tenure_months)
        if self.get('gold_items'):
            total_gross = sum((i.gross_weight or 0) for i in self.gold_items)
            total_net = sum((i.net_weight or 0) for i in self.gold_items)
            total_value = sum((i.item_value or 0) for i in self.gold_items)
            self.total_gross_weight = total_gross
            self.total_net_weight = total_net
            self.total_gold_value = total_value
            if total_value:
                self.ltv_ratio = round((self.loan_amount / total_value) * 100, 2)

