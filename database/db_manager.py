from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


class DatabaseManager:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS journal_transactions (
            transaction_id TEXT PRIMARY KEY, document_id TEXT NOT NULL, content_hash TEXT NOT NULL,
            company_code TEXT, payload_json TEXT NOT NULL, validation_json TEXT NOT NULL,
            reasoning_json TEXT NOT NULL, recommendation_json TEXT NOT NULL,
            validation_status TEXT NOT NULL, risk_level TEXT NOT NULL, state TEXT NOT NULL,
            sap_document_number TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS agent_execution_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT, transaction_id TEXT NOT NULL REFERENCES journal_transactions(transaction_id),
            agent_name TEXT NOT NULL, action TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS approval_history (
            approval_id INTEGER PRIMARY KEY AUTOINCREMENT, transaction_id TEXT NOT NULL REFERENCES journal_transactions(transaction_id),
            decision TEXT NOT NULL, actor TEXT NOT NULL, comment TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS posting_history (
            posting_id INTEGER PRIMARY KEY AUTOINCREMENT, transaction_id TEXT NOT NULL REFERENCES journal_transactions(transaction_id),
            sap_document_number TEXT NOT NULL UNIQUE, posting_status TEXT NOT NULL, actor TEXT NOT NULL, posted_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_transactions_state ON journal_transactions(state);
        CREATE INDEX IF NOT EXISTS idx_agent_logs_transaction ON agent_execution_logs(transaction_id);
        """
        with self._connect() as connection:
            connection.executescript(schema)

    def save_transaction(self, transaction: dict[str, Any]) -> None:
        now = self._now()
        company = next((str(line.get("company_code")) for line in transaction["payload"]["lines"] if line.get("company_code")), None)
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO journal_transactions
                (transaction_id, document_id, content_hash, company_code, payload_json, validation_json,
                 reasoning_json, recommendation_json, validation_status, risk_level, state, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (transaction["transaction_id"], transaction["document_id"], transaction["content_hash"], company,
                 self._dump(transaction["payload"]), self._dump(transaction["validation"]),
                 self._dump(transaction["reasoning"]), self._dump(transaction["recommendation"]),
                 "VALID" if transaction["validation"]["is_valid"] else "FAILED", transaction["recommendation"]["risk_level"],
                 transaction["state"], now, now),
            )
            for log in transaction["logs"]:
                connection.execute("INSERT INTO agent_execution_logs (transaction_id, agent_name, action, details, created_at) VALUES (?, ?, ?, ?, ?)",
                                   (transaction["transaction_id"], log["agent_name"], log["action"], log["details"], now))

    def get_existing_hashes(self) -> set[str]:
        with self._connect() as connection:
            return {row[0] for row in connection.execute("SELECT content_hash FROM journal_transactions")}

    def get_transaction(self, transaction_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM journal_transactions WHERE transaction_id = ?", (transaction_id,)).fetchone()
        return self._decode(row) if row else None

    def list_transactions(self, states: list[str] | None = None) -> list[dict[str, Any]]:
        query, parameters = "SELECT * FROM journal_transactions", ()
        if states:
            query += " WHERE state IN (" + ",".join("?" for _ in states) + ")"
            parameters = tuple(states)
        with self._connect() as connection:
            rows = connection.execute(query + " ORDER BY created_at DESC", parameters).fetchall()
        return [self._decode(row) for row in rows]

    def dashboard_summary(self) -> dict[str, int]:
        with self._connect() as connection:
            total = connection.execute("SELECT COUNT(*) FROM journal_transactions").fetchone()[0]
            states = dict(connection.execute("SELECT state, COUNT(*) FROM journal_transactions GROUP BY state").fetchall())
            valid = connection.execute("SELECT COUNT(*) FROM journal_transactions WHERE validation_status='VALID'").fetchone()[0]
        return {"total": total, "valid": valid, "validation_failures": states.get("VALIDATION_FAILED", 0),
                "pending_approvals": states.get("PENDING_APPROVAL", 0), "approved": states.get("APPROVED", 0), "posted": states.get("POSTED", 0)}

    def record_approval(self, transaction_id: str, actor: str, decision: str, comment: str = "") -> dict[str, Any]:
        if decision not in {"APPROVED", "REJECTED"}:
            raise ValueError("Approval decision must be APPROVED or REJECTED.")
        now = self._now()
        with self._connect() as connection:
            cursor = connection.execute("UPDATE journal_transactions SET state=?, updated_at=? WHERE transaction_id=? AND state='PENDING_APPROVAL' AND validation_status='VALID'",
                                        (decision, now, transaction_id))
            if cursor.rowcount != 1:
                self._raise_transition_error(connection, transaction_id, "Only valid journals pending approval can be approved or rejected.")
            connection.execute("INSERT INTO approval_history (transaction_id, decision, actor, comment, created_at) VALUES (?, ?, ?, ?, ?)",
                               (transaction_id, decision, actor, comment, now))
            connection.execute("INSERT INTO agent_execution_logs (transaction_id, agent_name, action, details, created_at) VALUES (?, ?, ?, ?, ?)",
                               (transaction_id, "Approval and Posting Agent", decision, comment or f"Decision recorded by {actor}.", now))
        result = self.get_transaction(transaction_id)
        if result is None:
            raise ValueError(f"Unknown transaction: {transaction_id}")
        return result

    def record_simulated_posting(self, transaction_id: str, actor: str) -> dict[str, Any]:
        now = self._now()
        with self._connect() as connection:
            row = connection.execute("SELECT state, validation_status FROM journal_transactions WHERE transaction_id=?", (transaction_id,)).fetchone()
            if row is None:
                raise ValueError(f"Unknown transaction: {transaction_id}")
            if row["state"] != "APPROVED" or row["validation_status"] != "VALID":
                raise ValueError("Only valid, approved transactions can be simulated for posting.")
            number = connection.execute("SELECT COUNT(*) + 1 FROM posting_history").fetchone()[0]
            document_number = f"SAP-SIM-{datetime.now(timezone.utc).year}-{number:06d}"
            connection.execute("INSERT INTO posting_history (transaction_id, sap_document_number, posting_status, actor, posted_at) VALUES (?, ?, 'SIMULATED', ?, ?)",
                               (transaction_id, document_number, actor, now))
            cursor = connection.execute("UPDATE journal_transactions SET state='POSTED', sap_document_number=?, updated_at=? WHERE transaction_id=? AND state='APPROVED' AND validation_status='VALID'",
                                        (document_number, now, transaction_id))
            if cursor.rowcount != 1:
                raise ValueError("Posting was not recorded because the transaction is no longer approved.")
            connection.execute("INSERT INTO agent_execution_logs (transaction_id, agent_name, action, details, created_at) VALUES (?, ?, ?, ?, ?)",
                               (transaction_id, "Approval and Posting Agent", "SIMULATED_POSTING", f"Simulated SAP document {document_number}; no SAP connection was used.", now))
        return self.get_transaction(transaction_id)

    def audit_history(self) -> dict[str, list[dict[str, Any]]]:
        with self._connect() as connection:
            logs = [dict(row) for row in connection.execute("SELECT * FROM agent_execution_logs ORDER BY created_at DESC, log_id DESC")]
            approvals = [dict(row) for row in connection.execute("SELECT * FROM approval_history ORDER BY created_at DESC, approval_id DESC")]
            postings = [dict(row) for row in connection.execute("SELECT * FROM posting_history ORDER BY posted_at DESC, posting_id DESC")]
        return {"agent_logs": logs, "approvals": approvals, "postings": postings}

    @staticmethod
    def _raise_transition_error(connection: sqlite3.Connection, transaction_id: str, message: str) -> None:
        if connection.execute("SELECT 1 FROM journal_transactions WHERE transaction_id=?", (transaction_id,)).fetchone() is None:
            raise ValueError(f"Unknown transaction: {transaction_id}")
        raise ValueError(message)

    @staticmethod
    def _decode(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        for key in ("payload", "validation", "reasoning", "recommendation"):
            result[key] = json.loads(result.pop(key + "_json"))
        return result

    @staticmethod
    def _dump(value: Any) -> str:
        return json.dumps(value, ensure_ascii=True, default=str)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
