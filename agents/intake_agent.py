from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd


class JournalIntakeAgent:
    """Loads CSV journal lines and groups them into documents."""

    def read_csv(self, source: Any) -> pd.DataFrame:
        if isinstance(source, (str, Path)) and not Path(source).is_file():
            raise FileNotFoundError(f"CSV file not found: {source}")
        try:
            frame = pd.read_csv(BytesIO(source)) if isinstance(source, bytes) else pd.read_csv(source)
        except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
            raise ValueError(f"Unable to read journal CSV: {exc}") from exc
        if frame.empty:
            raise ValueError("The uploaded CSV contains no journal lines.")
        frame.columns = [str(column).strip().lower() for column in frame.columns]
        return frame

    def prepare_records(self, frame: pd.DataFrame) -> list[dict[str, Any]]:
        if frame.empty:
            raise ValueError("There are no journal lines to process.")
        normalized = frame.copy()
        normalized.columns = [str(column).strip().lower() for column in normalized.columns]
        if "document_id" not in normalized:
            normalized["document_id"] = None
        for column in ("company_code", "gl_account", "cost_center", "debit", "credit", "currency", "description"):
            if column not in normalized:
                normalized[column] = None
        if "line_number" not in normalized:
            normalized["line_number"] = range(1, len(normalized) + 1)

        missing_document = normalized["document_id"].isna() | normalized["document_id"].astype(str).str.strip().eq("")
        normalized["_document_id_missing"] = missing_document
        normalized["document_id"] = normalized["document_id"].where(~missing_document, "")
        normalized["document_id"] = normalized["document_id"].astype(str).str.strip()
        for index in normalized.index[missing_document]:
            normalized.at[index, "document_id"] = f"MISSING-{index + 1}"

        documents = []
        for document_id, group in normalized.groupby("document_id", sort=False, dropna=False):
            lines = [{key: self._clean_value(value) for key, value in row.items()} for row in group.to_dict(orient="records")]
            documents.append({"transaction_id": str(uuid4()), "document_id": str(document_id), "lines": lines})
        return documents

    @staticmethod
    def _clean_value(value: Any) -> Any:
        if pd.isna(value):
            return None
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value.item() if hasattr(value, "item") else value
