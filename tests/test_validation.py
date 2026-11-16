import pandas as pd

from agents.intake_agent import JournalIntakeAgent
from agents.validation_agent import FinancialValidationAgent
from config import KNOWLEDGE_BASE_PATH
from knowledge_base.knowledge_service import KnowledgeService


def validate_lines(lines):
    intake = JournalIntakeAgent()
    document = intake.prepare_records(pd.DataFrame(lines))[0]
    return FinancialValidationAgent(KnowledgeService(KNOWLEDGE_BASE_PATH)).validate(document)


def two_lines(gl="500100", cost="CC200", company="IN01", debit=100, credit=100):
    return [
        {"document_id": "T1", "company_code": company, "gl_account": gl, "cost_center": cost, "debit": debit, "credit": 0},
        {"document_id": "T1", "company_code": "IN01", "gl_account": "100100", "cost_center": "CC200", "debit": 0, "credit": credit},
    ]


def test_balanced_journal_is_valid():
    assert validate_lines(two_lines())["is_valid"]


def test_unbalanced_journal_fails():
    assert "UNBALANCED" in {item["code"] for item in validate_lines(two_lines(credit=90))["errors"]}


def test_invalid_gl_account_fails():
    assert "INVALID_GL" in {item["code"] for item in validate_lines(two_lines(gl="999999"))["errors"]}


def test_invalid_cost_centre_fails():
    assert "INVALID_COST_CENTER" in {item["code"] for item in validate_lines(two_lines(cost="CC999"))["errors"]}


def test_missing_mandatory_fields_fail():
    errors = validate_lines(two_lines(company=None))["errors"]
    assert "MISSING_FIELD" in {item["code"] for item in errors}


def test_high_value_requires_additional_approval():
    assert validate_lines(two_lines(debit=1_000_001, credit=1_000_001))["high_value"]


def test_missing_document_id_fails():
    rows = two_lines()
    rows[0]["document_id"] = None
    assert "MISSING_FIELD" in {item["code"] for item in validate_lines(rows)["errors"]}


def test_csv_upload_bytes_are_read():
    frame = JournalIntakeAgent().read_csv(b"document_id,debit,credit\nB1,10,10\n")
    assert frame.loc[0, "document_id"] == "B1"
