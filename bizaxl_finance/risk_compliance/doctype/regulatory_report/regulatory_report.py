import json
import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months, format_date, flt, add_days
from frappe import _


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
            "ALM Report": self._generate_alm_report,
        }

        generator = report_generators.get(self.report_type)
        if generator:
            generator()

    # ── CRILC: Large Exposures (Rs.5Cr+) ──────────────────────────────────

    def _generate_crilc_report(self):
        """CRILC: RBI reporting for exposures Rs.5Cr+"""
        large_exposures = frappe.db.sql("""
            SELECT la.name, la.customer, la.loan_amount, la.outstanding_amount,
                   bc.customer_name, bc.pan_number, la.status
            FROM `tabLoan Application` la
            INNER JOIN `tabBizaxl Customer` bc ON bc.name = la.customer
            WHERE la.loan_amount >= 50000000
              AND la.status IN ('Disbursed', 'Approved')
        """, as_dict=True)

        self.set("remarks", json.dumps({
            "report_type": "CRILC",
            "generated_on": str(today()),
            "reporting_period": self.reporting_period,
            "period_start": str(self.period_start),
            "period_end": str(self.period_end),
            "total_exposures": len(large_exposures),
            "total_exposure_amount": sum(float(d.outstanding_amount or d.loan_amount or 0) for d in large_exposures),
            "exposures": [{k: str(v) for k, v in d.items()} for d in large_exposures],
            "reporting_frequency": "Monthly (due 7th of next month)",
            "submission_format": "RBI CRILC Portal",
        }, indent=2))

    # ── FPC: Financial Position Compliance ────────────────────────────────

    def _generate_fpc_report(self):
        """FPC: Financial Position Compliance report for Board approval"""
        # Get capital and liquidity metrics from accounting
        total_assets = frappe.db.sql("""
            SELECT COALESCE(SUM(debit - credit), 0) as total
            FROM `tabGL Entry`
            WHERE company = (SELECT company FROM `tabGL Settings` LIMIT 1)
              AND posting_date <= %s
        """, self.period_end or today())[0][0]

        total_liabilities = frappe.db.sql("""
            SELECT COALESCE(SUM(credit - debit), 0) as total
            FROM `tabGL Entry`
            WHERE is_liability = 1
              AND posting_date <= %s
        """, self.period_end or today())[0][0]

        capital_ratio = flt(total_assets / total_liabilities * 100) if total_liabilities else 0

        self.set("remarks", json.dumps({
            "report_type": "FPC Report",
            "generated_on": str(today()),
            "period": f"{self.period_start or 'N/A'} to {self.period_end or 'N/A'}",
            "total_assets": flt(total_assets),
            "total_liabilities": flt(total_liabilities),
            "capital_adequacy_ratio": round(capital_ratio, 2),
            "min_required_ratio": "15% (RBI NBFC)",
            "status": "Compliant" if capital_ratio >= 15 else "Non-Compliant",
            "board_approval_date": str(today()),
            "next_due_date": str(add_months(today(), 3)),
        }, indent=2))

    # ── PSL: Priority Sector Lending ─────────────────────────────────────

    def _generate_psl_report(self):
        """PSL: Priority Sector Lending report with percentage calculation"""
        psl_data = frappe.db.sql("""
            SELECT 
                CASE 
                    WHEN loan_type IN ('Agriculture', 'Agri') THEN 'Agriculture'
                    WHEN loan_type IN ('MSME', 'Business', 'Business Loan') THEN 'MSME'
                    WHEN loan_type IN ('Education', 'Education Loan') THEN 'Education'
                    WHEN loan_type IN ('Home Loan', 'Housing') THEN 'Housing'
                    WHEN loan_type IN ('Renewable Energy', 'Solar') THEN 'Renewable Energy'
                    ELSE 'Other'
                END as psl_category,
                COUNT(*) as count,
                SUM(loan_amount) as total
            FROM `tabLoan Application`
            WHERE status = 'Disbursed'
            GROUP BY psl_category
        """, as_dict=True)

        total_portfolio = frappe.db.sql("""
            SELECT COALESCE(SUM(loan_amount), 0) as total
            FROM `tabLoan Application`
            WHERE status = 'Disbursed'
        """)[0][0]

        psl_total = sum(float(d.total or 0) for d in psl_data if d.psl_category != "Other")
        psl_percentage = round(psl_total / total_portfolio * 100, 2) if total_portfolio else 0

        self.set("remarks", json.dumps({
            "report_type": "PSL Report",
            "generated_on": str(today()),
            "period": f"{self.period_start or 'N/A'} to {self.period_end or 'N/A'}",
            "total_portfolio": flt(total_portfolio),
            "psl_total": flt(psl_total),
            "psl_percentage": psl_percentage,
            "rbi_target": "40% of total ACF",
            "shortfall": max(0, round(40 - psl_percentage, 2)),
            "psl_breakdown": [
                {"category": d.psl_category, "count": d.count, "amount": float(d.total or 0)}
                for d in psl_data
            ],
        }, indent=2))

    # ── FIU-IND Cash Transaction Report ──────────────────────────────────

    def _generate_fiu_ctr(self):
        """FIU-IND CTR: Cash Transaction Report (Rs.10L+ / foreign remittance)"""
        # Check transactions from all payment-related DocTypes
        transactions = frappe.db.sql("""
            SELECT t.name, t.customer, t.transaction_date, t.amount,
                   t.transaction_type, t.description, bc.customer_name, bc.pan_number
            FROM `tabTransaction` t
            INNER JOIN `tabBizaxl Customer` bc ON bc.name = t.customer
            WHERE t.amount >= 1000000
              AND t.docstatus = 1
            ORDER BY t.transaction_date DESC
        """, as_dict=True)

        # Also check cash-based loan disbursements
        cash_disbursements = frappe.db.sql("""
            SELECT ld.name, ld.disbursement_date, ld.disbursed_amount
            FROM `tabLoan Disbursement` ld
            WHERE ld.disbursement_mode = 'Cash'
              AND ld.disbursed_amount >= 1000000
        """, as_dict=True)

        all_transactions = []
        for t in transactions:
            all_transactions.append({
                "transaction_id": t.name,
                "customer_name": t.customer_name,
                "pan": t.pan_number,
                "date": str(t.transaction_date),
                "amount": float(t.amount),
                "type": t.transaction_type,
                "description": t.description,
            })
        for d in cash_disbursements:
            all_transactions.append({
                "transaction_id": d.name,
                "type": "Cash Disbursement",
                "date": str(d.disbursement_date),
                "amount": float(d.disbursed_amount),
            })

        self.set("remarks", json.dumps({
            "report_type": "FIU-IND CTR",
            "reporting_period": self.reporting_period,
            "period": f"{self.period_start or 'N/A'} to {self.period_end or 'N/A'}",
            "generated_on": str(today()),
            "threshold": "Rs.10,00,000 (Cash Transaction)",
            "total_transactions": len(all_transactions),
            "total_amount": sum(t["amount"] for t in all_transactions),
            "transactions": all_transactions,
            "filing_deadline": f"15th of next month (within {add_months(today(), 1)})",
            "remarks": "CTR to be filed via FIU-IND FINnet Gateway",
        }, indent=2))

    # ── FIU-IND Suspicious Transaction Report ─────────────────────────────

    def _generate_fiu_str(self):
        """FIU-IND STR: Suspicious Transaction Report"""
        # Get fraud alerts and suspicious transactions
        suspicious = frappe.db.get_all("Fraud Alert",
            filters={"severity": ["in", ["High", "Critical"]]},
            fields=["name", "customer_name", "alert_type", "description",
                    "creation", "severity"]
        )

        # Also check unusually large repayments
        large_repayments = frappe.db.sql("""
            SELECT lr.name, lr.payment_date, lr.amount, la.customer
            FROM `tabLoan Repayment` lr
            INNER JOIN `tabLoan Application` la ON la.name = lr.loan_application
            WHERE lr.amount >= 5000000
              AND lr.docstatus = 1
        """, as_dict=True)

        str_entries = []
        for s in suspicious:
            str_entries.append({
                "alert_id": s.name,
                "customer": s.customer_name,
                "type": s.alert_type,
                "description": s.description,
                "date": str(s.creation),
                "severity": s.severity,
            })

        self.set("remarks", json.dumps({
            "report_type": "FIU-IND STR",
            "generated_on": str(today()),
            "period": f"{self.period_start or 'N/A'} to {self.period_end or 'N/A'}",
            "total_suspicious_activities": len(str_entries) + len(large_repayments),
            "fraud_alerts": str_entries,
            "large_repayments": [
                {"id": r.name, "date": str(r.payment_date), "amount": float(r.amount)}
                for r in large_repayments
            ],
            "filing_deadline": "Within 7 days of identifying suspicious activity",
            "submission": "FIU-IND FINnet Portal",
        }, indent=2))

    # ── RBI NPA Return ────────────────────────────────────────────────────

    def _generate_npa_report(self):
        """NPA classification report with SMA/NPA bucket breakdown"""
        npa_data = frappe.db.sql("""
            SELECT 
                COALESCE(npa_category, 'Standard') as asset_classification,
                COUNT(*) as count,
                SUM(outstanding_amount) as total_outstanding,
                SUM(provision_amount) as total_provision
            FROM `tabNPA Classification`
            WHERE docstatus = 1
            GROUP BY npa_category
        """, as_dict=True)

        total_npa = sum(float(d.total_outstanding or 0) for d in npa_data 
                       if d.asset_classification in 
                       ['Sub-Standard', 'Doubtful', 'Loss'])
        total_portfolio = sum(float(d.total_outstanding or 0) for d in npa_data)
        gross_npa_ratio = round(total_npa / total_portfolio * 100, 2) if total_portfolio else 0

        self.set("remarks", json.dumps({
            "report_type": "RBI NPA Return",
            "generated_on": str(today()),
            "period": f"{self.period_start or 'N/A'} to {self.period_end or 'N/A'}",
            "classification_buckets": [
                {"category": d.asset_classification, "count": d.count,
                 "outstanding": float(d.total_outstanding or 0),
                 "provision": float(d.total_provision or 0)}
                for d in npa_data
            ],
            "gross_npa_amount": flt(total_npa),
            "gross_npa_ratio": gross_npa_ratio,
            "net_npa_ratio": round((total_npa - sum(float(d.total_provision or 0) for d in npa_data)) / total_portfolio * 100, 2) if total_portfolio else 0,
            "provision_coverage_ratio": round(sum(float(d.total_provision or 0) for d in npa_data) / total_npa * 100, 2) if total_npa else 0,
            "reporting_format": "RBI Master Direction on NPA",
        }, indent=2))

    # ── ALM: Asset Liability Management Report ────────────────────────────

    def _generate_alm_report(self):
        """ALM Report: Asset Liability gap analysis with maturity buckets

        Time buckets: 1-7 days, 8-14 days, 15-30 days, 1-3 months,
                      3-6 months, 6-12 months, 1-3 years, 3-5 years, 5+ years
        """
        period_end = self.period_end or today()

        # Assets: Expected loan repayments (inflows)
        loan_inflows = frappe.db.sql("""
            SELECT 
                CASE 
                    WHEN DATEDIFF(%s, COALESCE(first_emi_date, %s)) <= 7 THEN '1-7 days'
                    WHEN DATEDIFF(%s, COALESCE(first_emi_date, %s)) <= 14 THEN '8-14 days'
                    WHEN DATEDIFF(%s, COALESCE(first_emi_date, %s)) <= 30 THEN '15-30 days'
                    WHEN DATEDIFF(%s, COALESCE(first_emi_date, %s)) <= 90 THEN '1-3 months'
                    WHEN DATEDIFF(%s, COALESCE(first_emi_date, %s)) <= 180 THEN '3-6 months'
                    WHEN DATEDIFF(%s, COALESCE(first_emi_date, %s)) <= 365 THEN '6-12 months'
                    WHEN DATEDIFF(%s, COALESCE(first_emi_date, %s)) <= 1095 THEN '1-3 years'
                    WHEN DATEDIFF(%s, COALESCE(first_emi_date, %s)) <= 1825 THEN '3-5 years'
                    ELSE '5+ years'
                END as bucket,
                COALESCE(SUM(emi_amount), 0) as expected_inflow
            FROM `tabLoan Application`
            WHERE status = 'Disbursed'
            GROUP BY bucket
        """, [period_end]*10, as_dict=True)

        # Liabilities: Expected deposit outflows (for NBFCs taking deposits)
        total_disbursements = frappe.db.sql("""
            SELECT COALESCE(SUM(disbursed_amount), 0) as total
            FROM `tabLoan Disbursement`
            WHERE docstatus = 1
        """)[0][0]

        alm_buckets = [
            {"bucket": d.bucket, "inflows": float(d.expected_inflow or 0),
             "outflows": float(d.expected_inflow or 0) * 0.3,  # estimated operational outflow
             "gap": float(d.expected_inflow or 0) * 0.7}
            for d in loan_inflows
        ]

        cumulative_gap = 0
        for b in alm_buckets:
            cumulative_gap += b["gap"]
            b["cumulative_gap"] = round(cumulative_gap, 2)
            b["gap_to_total_assets_ratio"] = round(
                cumulative_gap / total_disbursements * 100, 2
            ) if total_disbursements else 0

        self.set("remarks", json.dumps({
            "report_type": "ALM Report",
            "generated_on": str(today()),
            "as_of_date": str(period_end),
            "maturity_buckets": alm_buckets,
            "total_assets": flt(total_disbursements),
            "liquidity_ratio": round(
                sum(b["inflows"] for b in alm_buckets[:3]) / 
                max(sum(b["outflows"] for b in alm_buckets[:3]), 1) * 100, 2
            ),
            "recommendations": self._generate_alm_recommendations(alm_buckets),
            "next_review_date": str(add_months(period_end, 1)),
        }, indent=2))

    def _generate_alm_recommendations(self, buckets):
        """Generate ALM recommendations based on gap analysis"""
        recs = []
        for b in buckets:
            if b["gap_to_total_assets_ratio"] < -10:
                recs.append(f"Negative gap in {b['bucket']} bucket: {b['gap_to_total_assets_ratio']}%")
        if not recs:
            recs.append("All maturity buckets within acceptable limits")
        return recs

    # ── Board Report ──────────────────────────────────────────────────────

    def _generate_board_report(self):
        """Board-level report with portfolio KPIs, credit committee summary, and analytics"""
        period_end = self.period_end or today()
        period_start = self.period_start or add_months(period_end, -1)

        # Portfolio overview
        portfolio = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_loans,
                COALESCE(SUM(loan_amount), 0) as total_sanctioned,
                COALESCE(SUM(CASE WHEN status = 'Disbursed' THEN outstanding_amount ELSE 0 END), 0) as total_outstanding,
                COUNT(CASE WHEN status IN ('Disbursed', 'Approved') THEN 1 END) as active_loans
            FROM `tabLoan Application`
        """, as_dict=True)[0]

        # Vertical-wise breakdown
        vertical_breakdown = frappe.db.sql("""
            SELECT loan_type, COUNT(*) as count, 
                   COALESCE(SUM(loan_amount), 0) as total
            FROM `tabLoan Application`
            WHERE status = 'Disbursed'
            GROUP BY loan_type
        """, as_dict=True)

        # Credit committee decisions
        committee_decisions = frappe.db.sql("""
            SELECT decision, COUNT(*) as count
            FROM `tabCredit Committee Decision`
            WHERE decision_date BETWEEN %s AND %s
            GROUP BY decision
        """, (period_start, period_end), as_dict=True)

        # Recent fraud alerts for board attention
        recent_frauds = frappe.db.get_all("Fraud Alert",
            filters={"creation": [">=", period_start]},
            fields=["name", "customer_name", "alert_type", "severity", "creation"],
            order_by="creation desc",
            limit=10
        )

        # NPA snapshot
        npa_stats = frappe.db.sql("""
            SELECT npa_category, COUNT(*) as count,
                   COALESCE(SUM(outstanding_amount), 0) as total
            FROM `tabNPA Classification`
            WHERE docstatus = 1
            GROUP BY npa_category
        """, as_dict=True)

        self.set("remarks", json.dumps({
            "report_type": "Board Report",
            "generated_on": str(today()),
            "reporting_period": f"{period_start} to {period_end}",
            "portfolio_summary": {
                "total_loans": portfolio.total_loans,
                "total_sanctioned": float(portfolio.total_sanctioned or 0),
                "total_outstanding": float(portfolio.total_outstanding or 0),
                "active_loans": portfolio.active_loans,
            },
            "vertical_breakdown": [
                {"vertical": d.loan_type, "count": d.count, "amount": float(d.total or 0)}
                for d in vertical_breakdown
            ],
            "credit_committee_summary": [
                {"decision": d.decision, "count": d.count} for d in committee_decisions
            ],
            "fraud_alerts": [
                {"id": f.name, "customer": f.customer_name, "type": f.alert_type,
                 "severity": f.severity, "date": str(f.creation)}
                for f in recent_frauds
            ],
            "npa_snapshot": [
                {"category": d.npa_category, "count": d.count, "amount": float(d.total or 0)}
                for d in npa_stats
            ],
            "board_attention_items": self._get_board_attention_items(period_start, period_end),
        }, indent=2))

    def _get_board_attention_items(self, from_date, to_date):
        """Identify items requiring board attention"""
        items = []
        # High-value sanctions
        high_value = frappe.db.count("Loan Application", {
            "status": ["in", ["Approved", "Disbursed"]],
            "loan_amount": [">=", 10000000],
            "approval_date": ["between", (from_date, to_date)],
        })
        if high_value:
            items.append(f"{high_value} high-value loans (Rs.1Cr+) approved this period")

        # Critical fraud alerts
        critical_frauds = frappe.db.count("Fraud Alert", {
            "severity": "Critical",
            "creation": [">=", from_date],
        })
        if critical_frauds:
            items.append(f"{critical_frauds} Critical fraud alerts require board review")

        # NPA increase
        new_npas = frappe.db.count("NPA Classification", {
            "npa_category": ["in", ["Sub-Standard", "Doubtful", "Loss"]],
            "creation": [">=", from_date],
        })
        if new_npas:
            items.append(f"{new_npas} new NPA accounts classified")

        if not items:
            items.append("No critical items requiring immediate board attention")

        return items
