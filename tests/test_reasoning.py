from config import KNOWLEDGE_BASE_PATH
from knowledge_base.knowledge_service import KnowledgeService


def test_reasoning_matches_invalid_gl_policy():
    policies = KnowledgeService(KNOWLEDGE_BASE_PATH).evaluate([{"code": "INVALID_GL", "message": "bad account"}])
    assert "GL_MASTER" in {policy["id"] for policy in policies}


def test_high_value_policy_explains_additional_approval():
    policies = KnowledgeService(KNOWLEDGE_BASE_PATH).evaluate([], high_value=True)
    assert any("additional finance approval" in item["explanation"].lower() for item in policies)
