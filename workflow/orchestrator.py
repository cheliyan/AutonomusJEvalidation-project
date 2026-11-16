from __future__ import annotations

from typing import Any

from agents.approval_posting_agent import ApprovalPostingAgent
from agents.intake_agent import JournalIntakeAgent
from agents.reasoning_agent import KnowledgeReasoningAgent
from agents.recommendation_agent import RecommendationAgent
from agents.validation_agent import FinancialValidationAgent


class FinanceWorkflowOrchestrator:
    def __init__(self, knowledge_service, db_manager):
        self.knowledge_service = knowledge_service
        self.db_manager = db_manager
        self.intake_agent = JournalIntakeAgent()
        self.validation_agent = FinancialValidationAgent(knowledge_service)
        self.reasoning_agent = KnowledgeReasoningAgent(knowledge_service)
        self.recommendation_agent = RecommendationAgent(knowledge_service)
        self.approval_posting_agent = ApprovalPostingAgent(db_manager)

    def process_csv(self, source: Any) -> list[dict[str, Any]]:
        return self.process_dataframe(self.intake_agent.read_csv(source))

    def process_dataframe(self, frame) -> list[dict[str, Any]]:
        documents = self.intake_agent.prepare_records(frame)
        hashes = self.db_manager.get_existing_hashes()
        results = []
        for document in documents:
            validation = self.validation_agent.validate(document, hashes)
            hashes.add(validation["content_hash"])
            reasoning = self.reasoning_agent.explain(validation)
            recommendation = self.recommendation_agent.recommend(validation, reasoning)
            state = "PENDING_APPROVAL" if validation["is_valid"] else "VALIDATION_FAILED"
            logs = [
                {"agent_name": "Journal Intake Agent", "action": "RECEIVED", "details": f"Read {len(document['lines'])} line(s) for {document['document_id']}."},
                {"agent_name": "Financial Validation Agent", "action": "VALIDATED", "details": f"{len(validation['errors'])} validation issue(s); result {validation['is_valid']}."},
                {"agent_name": reasoning["agent"], "action": "POLICY_EVALUATED", "details": reasoning["explanation"]},
                {"agent_name": recommendation["agent"], "action": recommendation["decision"], "details": recommendation["recommendation"]},
            ]
            record = {"transaction_id": document["transaction_id"], "document_id": document["document_id"],
                      "content_hash": validation["content_hash"], "payload": document, "validation": validation,
                      "reasoning": reasoning, "recommendation": recommendation, "state": state, "logs": logs}
            self.db_manager.save_transaction(record)
            results.append(self.db_manager.get_transaction(document["transaction_id"]))
        return results

    def approve(self, transaction_id: str, actor: str = "Finance Approver") -> dict[str, Any]:
        return self.approval_posting_agent.approve(transaction_id, actor)

    def reject(self, transaction_id: str, actor: str = "Finance Approver", comment: str = "") -> dict[str, Any]:
        return self.approval_posting_agent.reject(transaction_id, actor, comment)

    def post(self, transaction_id: str, actor: str = "Posting Agent") -> dict[str, Any]:
        return self.approval_posting_agent.post(transaction_id, actor)
