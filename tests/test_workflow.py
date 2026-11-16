import pandas as pd
import pytest

from config import KNOWLEDGE_BASE_PATH
from database.db_manager import DatabaseManager
from knowledge_base.knowledge_service import KnowledgeService
from workflow.orchestrator import FinanceWorkflowOrchestrator


@pytest.fixture
def workflow(tmp_path):
    database = DatabaseManager(tmp_path / "finance_test.db")
    return FinanceWorkflowOrchestrator(KnowledgeService(KNOWLEDGE_BASE_PATH), database)


def valid_journal(document_id="WF-1"):
    return pd.DataFrame([
        {"document_id": document_id, "company_code": "IN01", "gl_account": "500100", "cost_center": "CC200", "debit": 250, "credit": 0, "description": document_id},
        {"document_id": document_id, "company_code": "IN01", "gl_account": "100100", "cost_center": "CC200", "debit": 0, "credit": 250, "description": document_id},
    ])


def test_approval_and_rejection_are_recorded(workflow):
    frame = pd.concat([valid_journal("WF-2"), valid_journal("WF-3")], ignore_index=True)
    approved, rejected = workflow.process_dataframe(frame)
    assert workflow.approve(approved["transaction_id"])["state"] == "APPROVED"
    assert workflow.reject(rejected["transaction_id"], comment="Missing support")["state"] == "REJECTED"


def test_posting_is_prevented_without_approval(workflow):
    transaction = workflow.process_dataframe(valid_journal())[0]
    with pytest.raises(ValueError, match="Only valid, approved"):
        workflow.post(transaction["transaction_id"])


def test_successful_simulated_posting(workflow):
    transaction = workflow.process_dataframe(valid_journal())[0]
    workflow.approve(transaction["transaction_id"])
    posted = workflow.post(transaction["transaction_id"])
    assert posted["state"] == "POSTED"
    assert posted["sap_document_number"].startswith("SAP-SIM-")
    assert workflow.db_manager.audit_history()["postings"][0]["posting_status"] == "SIMULATED"


def test_validation_failure_cannot_be_approved(workflow):
    lines = valid_journal("WF-BAD")
    lines.loc[1, "credit"] = 200
    transaction = workflow.process_dataframe(lines)[0]
    with pytest.raises(ValueError, match="Only valid journals"):
        workflow.approve(transaction["transaction_id"])
