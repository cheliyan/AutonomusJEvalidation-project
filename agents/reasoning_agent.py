from typing import Any


class KnowledgeReasoningAgent:
    def __init__(self, knowledge_service):
        self.knowledge_service = knowledge_service

    def explain(self, validation: dict[str, Any]) -> dict[str, Any]:
        policies = self.knowledge_service.evaluate(validation["errors"], validation["high_value"], validation["cross_company"])
        explanation = " ".join(policy["explanation"] for policy in policies) or "The journal passed configured balance, master-data, and policy checks."
        return {"applicable_policies": policies, "explanation": explanation, "agent": "Knowledge-Based Reasoning Agent"}
