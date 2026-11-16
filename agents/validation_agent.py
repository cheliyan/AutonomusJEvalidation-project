from __future__ import annotations

import hashlib
import json
from typing import Any


class FinancialValidationAgent:
    def __init__(self, knowledge_service):
        self.knowledge_service = knowledge_service

    def validate(self, document: dict[str, Any], known_hashes: set[str] | None = None) -> dict[str, Any]:
        rules = self.knowledge_service.rules
        errors: list[dict[str, str]] = []
        lines = document["lines"]
        debit_total = credit_total = 0.0
        companies: set[str] = set()
        intercompany_present = False
        for index, line in enumerate(lines, start=1):
            for field in rules["validation"]["required_fields"]:
                if field == "document_id" and line.get("_document_id_missing"):
                    errors.append(self._error("MISSING_FIELD", f"Line {index}: required field 'document_id' is missing."))
                elif self._missing(line.get(field)):
                    errors.append(self._error("MISSING_FIELD", f"Line {index}: required field '{field}' is missing."))
            company = self._text(line.get("company_code"))
            gl = self._text(line.get("gl_account"))
            cost = self._text(line.get("cost_center"))
            if company:
                companies.add(company)
                if company not in rules["masters"]["company_codes"]:
                    errors.append(self._error("INVALID_COMPANY_CODE", f"Line {index}: company code '{company}' is not in the company master."))
            if gl:
                if gl not in rules["masters"]["gl_accounts"]:
                    errors.append(self._error("INVALID_GL", f"Line {index}: GL account '{gl}' does not exist."))
                elif gl in rules["intercompany"]["gl_accounts"]:
                    intercompany_present = True
            if cost and cost not in rules["masters"]["cost_centres"]:
                errors.append(self._error("INVALID_COST_CENTER", f"Line {index}: cost centre '{cost}' does not exist."))
            debit, credit = self._amount(line.get("debit")), self._amount(line.get("credit"))
            if debit is None or credit is None:
                errors.append(self._error("INVALID_AMOUNT", f"Line {index}: debit and credit must be numeric."))
                continue
            if debit < 0 or credit < 0:
                errors.append(self._error("NEGATIVE_AMOUNT", f"Line {index}: amounts cannot be negative."))
            if debit > 0 and credit > 0:
                errors.append(self._error("BOTH_SIDES_POPULATED", f"Line {index}: enter an amount on debit or credit, not both."))
            if debit == 0 and credit == 0:
                errors.append(self._error("ZERO_AMOUNT", f"Line {index}: debit and credit cannot both be zero."))
            debit_total += debit
            credit_total += credit

        tolerance = rules["validation"]["balance_tolerance"]
        if abs(debit_total - credit_total) > tolerance:
            errors.append(self._error("UNBALANCED", f"Document debits ({debit_total:.2f}) do not equal credits ({credit_total:.2f})."))
        cross_company = len(companies) > 1
        if cross_company and not intercompany_present:
            errors.append(self._error("MISSING_INTERCOMPANY_ACCOUNT", "Cross-company journal requires an approved intercompany GL account."))
        content_hash = self._content_hash(lines)
        if known_hashes and content_hash in known_hashes:
            errors.append(self._error("DUPLICATE", "This journal has already been processed or appears more than once in this upload."))
        total_amount = max(debit_total, credit_total)
        return {
            "is_valid": not errors, "errors": errors,
            "debit_total": round(debit_total, 2), "credit_total": round(credit_total, 2),
            "total_amount": round(total_amount, 2), "cross_company": cross_company,
            "high_value": total_amount > rules["approval_thresholds"]["additional_approval_inr"],
            "content_hash": content_hash,
        }

    @staticmethod
    def _error(code: str, message: str) -> dict[str, str]:
        return {"code": code, "message": message}

    @staticmethod
    def _missing(value: Any) -> bool:
        return value is None or (isinstance(value, str) and not value.strip())

    @staticmethod
    def _text(value: Any) -> str:
        return "" if FinancialValidationAgent._missing(value) else str(value).strip()

    @staticmethod
    def _amount(value: Any) -> float | None:
        try:
            return None if value is None or str(value).strip() == "" else float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _content_hash(lines: list[dict[str, Any]]) -> str:
        fields = ("company_code", "gl_account", "cost_center", "debit", "credit", "currency", "description")
        content = [{key: line.get(key) for key in fields} for line in lines]
        serialized = json.dumps(content, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
