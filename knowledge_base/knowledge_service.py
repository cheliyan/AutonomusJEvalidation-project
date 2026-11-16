import json
from pathlib import Path
from typing import Any


class KnowledgeService:
    def __init__(self, knowledge_base_path: str | Path):
        path = Path(knowledge_base_path)
        try:
            self.rules = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Finance knowledge base not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid finance knowledge base JSON: {exc}") from exc
        required = {"rules", "validation", "masters", "intercompany", "approval_thresholds", "risk_classification"}
        missing = required.difference(self.rules)
        if missing:
            raise ValueError(f"Finance knowledge base is missing sections: {', '.join(sorted(missing))}")

    def evaluate(self, errors: list[dict[str, str]], high_value: bool = False, cross_company: bool = False) -> list[dict[str, Any]]:
        codes = {error["code"] for error in errors}
        policies = []
        for rule in self.rules["rules"]:
            matches = bool(codes.intersection(rule.get("error_codes", [])))
            matches |= rule["id"] == "HIGH_VALUE_APPROVAL" and high_value
            matches |= rule["id"] == "CROSS_COMPANY_INTERCOMPANY" and cross_company
            if matches:
                policies.append({key: rule[key] for key in ("id", "name", "explanation", "action")})
        return policies
