import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class BusinessProfile(Document):
    def validate(self):
        self.calculate_dscr()

    def calculate_dscr(self):
        """
        Calculate DSCR (Debt Service Coverage Ratio).

        Formula:
        DSCR = (Net Profit + Interest Expense + Depreciation) /
               (Interest Expense + Loan Principal Repayment)

        Thresholds:
        - DSCR >= 1.25: Healthy (Green)
        - DSCR >= 1.0: Acceptable (Amber)
        - DSCR < 1.0: Critical (Red) - Cash flow insufficient to service debt
        """
        net_profit = flt(self.net_profit or 0)
        interest_expense = flt(self.interest_expense or 0)
        depreciation = flt(self.depreciation or 0)
        loan_principal = flt(self.loan_principal_repayment or 0)

        # Total debt service = Interest + Principal repayment
        total_debt_service = interest_expense + loan_principal
        self.total_debt_service = total_debt_service

        if total_debt_service <= 0:
            self.dscr_value = 0
            self.dscr_calculation_date = today()
            return

        # EBITDA = Net Profit + Interest + Depreciation
        ebitda = net_profit + interest_expense + depreciation

        # DSCR = EBITDA / Total Debt Service
        dscr = ebitda / total_debt_service
        self.dscr_value = round(dscr, 4)
        self.dscr_calculation_date = today()

        # Status indicator
        if dscr >= 1.25:
            status = "Healthy"
            dscr_note = f"DSCR: {dscr:.2f} - {status}"
            if self.remarks:
                if dscr_note not in self.remarks:
                    self.remarks += f"\n{dscr_note}"
            else:
                self.remarks = dscr_note
        elif dscr >= 1.0:
            frappe.msgprint(
                f"⚠️ DSCR {dscr:.2f} is acceptable but below 1.25 threshold. "
                "Monitor cash flow closely.",
                alert=True, indicator="orange"
            )
        else:
            frappe.msgprint(
                f"❌ CRITICAL: DSCR {dscr:.2f} is below 1.0. "
                "Cash flow insufficient to service debt!",
                alert=True, indicator="red"
            )
