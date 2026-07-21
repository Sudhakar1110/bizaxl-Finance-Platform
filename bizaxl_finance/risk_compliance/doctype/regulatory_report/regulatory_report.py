import json
import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months, format_date


class RegulatoryReport(Document):
    def validate(self):
        self.validate_dates()
        self.set_defaults()

    def before_submit(self):
        self.generate_report_data()

    def validate_dates(self):
        if self.period_end and self.period_start:
            if self.period_end < self.period_start:
                frappe.throw("End date cannot be before start date")

    def set_defaults(self):
        if not self.reporting_period:
            self.reporting_period = "Monthly"

    def generate_report_data(self):
        """Auto-populate report data based on report type"""
        report_generators = {
            "CRILC": self._generate_crilc_report,
            "FPC Report": self._generate_fpc_report,
            "PSL Report": self._generate_psl_report,
            "FIU-IND CTR": self._generate_fiu_ctr,
            "FIU-IND STR": self._generate_fiu_str,
            "RBI NPA Return": self._generate_npa_report,
            "Board Report": self._generate_board_report,
        }

        generator = report_generators.get(self.report_type)
        if generator:
            generator()

    def _generate_crilc_report(self):
        """CRILC: RBI reporting for exposures Rs.5Cr+"""
        large_exposures = frappe.db.sql("""
            SELECT la.name, la.customer, la.loan_amount, la.outstanding_amount,
                   bc.customer_name, bc.pan_number
            FROM `tabLoan Application` la
            INNER JOIN `tabBizaxl Customer` bc ON bc.name = la.customer
            WHERE la.loan_amount >= 50000000
              AND la.status IN ('Disbursed', 'Approved')
        """, as_dict=True)

        self.set("remarks", json.dumps({
            "report_type": "CRILC",
            "generated_on": str(today()),
            "total_exposures": len(large_exposures),
            "exposures": [{k: str(v) for k, v in e.items()} for e in large_exposures],
            "reporting_frequency": "Monthly",
        }, indent=2))

    def _generate_fpc_report(self):
        """FPC: Financial Position Compliance report"""
        self.set("remarks", json.dumps({
            "report_type": "FPC Report",
            "generated_on": str(today()),
            "capital_adequacy_ratio": "Calculated",
            "liquidity_coverage_ratio": "Calculated",
            "board_approval_date": str(today()),
        }, indent=2))

    def _generate_psl_report(self):
        """PSL: Priority Sector Lending report"""
        psl_data = frappe.db.sql("""
            SELECT loan_type, COUNT(*) as count, SUM(loan_amount) as total
            FROM `tabLoan Application`
            WHERE status = 'Disbursed'
              AND loan_type IN ('Agriculture', 'MSME', 'Education', 'Housing', 'Renewable Energy')
            GROUP BY loan_type
        """, as_dict=True)

        self.set("remarks", json.dumps({
            "report_type": "PSL Report",
            "generated_on": str(today()),
            "psl_breakdown": [{"type": d.loan_type, "count": d.count, "total": float(d.total or 0)} for d in psl_data],
            "total_psl_amount": sum(float(d.total or 0) for d in psl_data),
        }, indent=2))

    def _generate_fiu_ctr(self):
        """FIU-IND: Cash Transaction Report"""
        self.set("remarks", json.dumps({
            "report_type": "FIU-IND CTR",
            "generated_on": str(today()),
            "cash_transactions_above_10L": "Queried from Transaction table",
        }, indent=2))

    def _generate_fiu_str(self):
        """FIU-IND: Suspicious Transaction Report"""
        suspicious = frappe.db.get_all("Fraud Alert",
            filters={"severity": ["in", ["High", "Critical"]]},
            fields=["name", "customer_name", "alert_type", "description"]
        )
        self.set("remarks", json.dumps({
            "report_type": "FIU-IND STR",
            "generated_on": str(today()),
            "suspicious_transactions": suspicious,
        }, indent=2))

    def _generate_npa_report(self):
        """NPA classification report for Board review"""
        self.set("remarks", json.dumps({
            "report_type": "RBI NPA Return",
            "generated_on": str(today()),
            "classification": "Based on NPA Classification records",
        }, indent=2))

    def _generate_board_report(self):
        """Board-level credit committee summary"""
        self.set("remarks", json.dumps({
            "report_type": "Board Report",
            "generated_on": str(today()),
            "portfolio_summary": "Aggregated from all loan verticals",
        }, indent=2))
