import json
import frappe
from frappe.model.document import Document

class ScorecardConfig(Document):
    def validate(self):
        self.validate_thresholds()
        self.validate_weights()

    def validate_thresholds(self):
        if self.min_score_for_approval and self.min_score_for_referral:
            if self.min_score_for_approval <= self.min_score_for_referral:
                frappe.throw(
                    "Min Score for Approval must be greater than Min Score for Referral"
                )

    def validate_weights(self):
        if self.scope_weights_json:
            try:
                weights = json.loads(self.scope_weights_json)
                total = sum(weights.values())
                if abs(total - 100) > 0.01:
                    frappe.msgprint(
                        f"Warning: Score weights total {total}%, expected 100%",
                        indicator="orange"
                    )
            except json.JSONDecodeError:
                frappe.throw("Invalid JSON in Score Weights Configuration")

    def get_default_weights(self):
        """Return default score weights if none configured"""
        return {
            "bureau_score": 35,
            "income_stability": 20,
            "repayment_history": 20,
            "employment_stability": 10,
            "existing_obligations": 10,
            "age_factor": 5,
        }

    def evaluate(self, applicant_data):
        """Evaluate an applicant using this scorecard configuration
        
        Args:
            applicant_data: dict with bureau_score, monthly_income, etc.
            
        Returns:
            dict with score, decision, and recommendation
        """
        score = self._calculate_score(applicant_data)
        return {
            "score": score,
            "max_score": self.max_score,
            "decision": self._get_decision(score),
            "recommendation": self._get_recommendation(score),
        }

    def _calculate_score(self, data):
        """Calculate weighted score from applicant data"""
        try:
            weights = json.loads(self.scope_weights_json) if self.scope_weights_json else {}
        except (json.JSONDecodeError, TypeError):
            weights = self.get_default_weights()

        score = 0
        # Bureau score contribution (normalized to 0-35)
        bureau = (data.get("bureau_score", 700) - 300) / 6  # Normalize 300-900 to 0-100
        score += min(bureau, 100) * weights.get("bureau_score", 35) / 100

        # Income stability (0-20)
        if data.get("years_in_current_job", 0) > 3:
            score += 20 * weights.get("income_stability", 20) / 100
        elif data.get("years_in_current_job", 0) > 1:
            score += 10 * weights.get("income_stability", 20) / 100

        return min(int(score), self.max_score or 100)

    def _get_decision(self, score):
        if score >= (self.min_score_for_approval or 70):
            return "Approve"
        elif score >= (self.min_score_for_referral or 50):
            return "Refer"
        else:
            return "Reject"

    def _get_recommendation(self, score):
        if score >= (self.min_score_for_approval or 70):
            if self.auto_decision_enabled and score >= 85:
                return "Auto-approve"
            return "Manual Approve"
        elif score >= (self.min_score_for_referral or 50):
            return "Manual Review Required"
        else:
            return "Auto-reject"
