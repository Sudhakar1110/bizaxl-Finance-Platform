from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InvestmentGoal(Document):
    def validate(self):
        self.check_goal_achievement()

    def check_goal_achievement(self):
        if self.current_savings and self.target_amount:
            if self.current_savings >= self.target_amount:
                self.status = "Achieved"
