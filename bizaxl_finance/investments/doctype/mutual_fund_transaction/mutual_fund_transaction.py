import frappe
from frappe.model.document import Document

class MutualFundTransaction(Document):
    def validate(self):
        self.set_customer_from_mf()

    def before_submit(self):
        self.update_mutual_fund_holdings()

    def set_customer_from_mf(self):
        if self.mutual_fund and not self.customer:
            mf = frappe.get_doc("Mutual Fund", self.mutual_fund)
            self.customer = mf.customer

    def update_mutual_fund_holdings(self):
        mf = frappe.get_doc("Mutual Fund", self.mutual_fund)
        if self.transaction_type in ["Purchase", "SIP", "Switch In"]:
            mf.units_held = (mf.units_held or 0) + (self.units or 0)
            mf.invested_amount = (mf.invested_amount or 0) + self.amount
        elif self.transaction_type in ["Redemption", "Switch Out"]:
            mf.units_held = (mf.units_held or 0) - (self.units or 0)
            mf.invested_amount = max(0, (mf.invested_amount or 0) - self.amount)
        mf.save()
