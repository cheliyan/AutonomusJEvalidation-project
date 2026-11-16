from typing import Any


class RecommendationAgent:
    def __init__(self, knowledge_service):
        self.knowledge_service = knowledge_service

    def recommend(self, validation: dict[str, Any], reasoning: dict[str, Any]) -> dict[str, str]:
        if validation["errors"]:
            risk, decision = "HIGH", "CORRECT_AND_RESUBMIT"
            recommendation = self._correction(validation["errors"])
        else:
            threshold = self.knowledge_service.rules["risk_classification"]["medium_min_inr"]
            risk = "HIGH" if validation["high_value"] else "MEDIUM" if validation["cross_company"] or validation["total_amount"] >= threshold else "LOW"
            decision = "APPROVAL_REQUIRED"
            if validation["high_value"]:
                recommendation = "High-value transaction: additional finance approval is required."
            elif risk == "MEDIUM":
                recommendation = "Route to a finance approver and confirm supporting documentation before posting."
            else:
                recommendation = "Journal passed automated checks; route it for standard human approval."
        return {"risk_level": risk, "decision": decision, "recommendation": recommendation,
                "explanation": reasoning["explanation"], "agent": "Recommendation Agent"}

    @staticmethod
    def _correction(errors: list[dict[str, str]]) -> str:
        codes = {error["code"] for error in errors}
        corrections = (
            ({"INVALID_GL"}, "GL account does not exist. Please verify the account against the GL master."),
            ({"INVALID_COST_CENTER"}, "Cost centre does not exist. Please select an approved cost centre."),
            ({"MISSING_FIELD", "INVALID_COMPANY_CODE"}, "Required company or journal data is missing or invalid. Complete it using approved master data."),
            ({"UNBALANCED"}, "Debit and credit amounts are not equal. Please correct the journal amounts."),
            ({"MISSING_INTERCOMPANY_ACCOUNT"}, "Add a valid intercompany GL account to the cross-company journal."),
            ({"DUPLICATE"}, "This journal appears to be a duplicate. Confirm the source document before resubmitting."),
            ({"NEGATIVE_AMOUNT", "BOTH_SIDES_POPULATED", "ZERO_AMOUNT", "INVALID_AMOUNT"}, "Correct the debit and credit amounts; each line must contain one non-negative amount."),
        )
        for matching, text in corrections:
            if codes.intersection(matching):
                return text
        return "Resolve the validation issues listed for this journal before resubmitting."
