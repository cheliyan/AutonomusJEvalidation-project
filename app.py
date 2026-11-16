from __future__ import annotations

import sqlite3

import pandas as pd
import streamlit as st

from config import DATABASE_PATH, KNOWLEDGE_BASE_PATH
from database.db_manager import DatabaseManager
from knowledge_base.knowledge_service import KnowledgeService
from workflow.orchestrator import FinanceWorkflowOrchestrator

st.set_page_config(page_title="Finance Workflow Automation", page_icon="📊", layout="wide")


@st.cache_resource
def get_workflow():
    return FinanceWorkflowOrchestrator(KnowledgeService(KNOWLEDGE_BASE_PATH), DatabaseManager(DATABASE_PATH))


def display_transactions(transactions):
    rows = []
    for item in transactions:
        lines = item["payload"]["lines"]
        rows.append({
            "Transaction ID": item["transaction_id"], "Document": item["document_id"],
            "Company code(s)": ", ".join(sorted({str(line.get("company_code")) for line in lines if line.get("company_code")})) or "Missing",
            "GL account(s)": ", ".join(sorted({str(line.get("gl_account")) for line in lines if line.get("gl_account")})),
            "Cost centre(s)": ", ".join(sorted({str(line.get("cost_center")) for line in lines if line.get("cost_center")})),
            "Debit (INR)": item["validation"]["debit_total"], "Credit (INR)": item["validation"]["credit_total"],
            "Validation": item["validation_status"], "Risk": item["risk_level"], "State": item["state"],
            "Recommendation": item["recommendation"]["recommendation"], "Reasoning": item["reasoning"]["explanation"],
        })
    return rows


def dashboard(workflow):
    st.title("Finance Operations Dashboard")
    st.caption("Journal control, approvals, and simulated posting activity")
    summary = workflow.db_manager.dashboard_summary()
    columns = st.columns(6)
    for column, label, key in zip(columns, ("Processed", "Valid", "Failures", "Pending", "Approved", "Posted"),
                                  ("total", "valid", "validation_failures", "pending_approvals", "approved", "posted")):
        column.metric(label, summary[key])
    transactions = workflow.db_manager.list_transactions()
    if not transactions:
        st.info("No journal transactions yet. Upload the sample CSV to begin.")
        return
    left, right = st.columns(2)
    left.subheader("Transaction status")
    left.bar_chart(pd.Series([item["state"] for item in transactions]).value_counts())
    right.subheader("Risk classification")
    right.bar_chart(pd.Series([item["risk_level"] for item in transactions]).value_counts())
    st.subheader("Recent journal documents")
    st.dataframe(pd.DataFrame(display_transactions(transactions[:10])), width="stretch", hide_index=True)


def upload_page(workflow):
    st.title("Journal Upload")
    uploaded = st.file_uploader("Upload journal lines (CSV)", type=["csv"])
    if uploaded is None:
        st.info("Choose a CSV file, or use `data/sample_journal_entries.csv`.")
        return
    try:
        preview = workflow.intake_agent.read_csv(uploaded.getvalue())
    except (ValueError, FileNotFoundError) as exc:
        st.error(str(exc))
        return
    st.subheader("Uploaded journal lines")
    st.dataframe(preview, width="stretch", hide_index=True)
    if st.button("Process Transactions", type="primary"):
        try:
            results = workflow.process_dataframe(preview)
            st.session_state["last_processed_ids"] = [item["transaction_id"] for item in results]
            st.success(f"Processed {len(results)} journal document(s).")
        except (ValueError, sqlite3.Error) as exc:
            st.error(f"Processing failed: {exc}")
    if st.session_state.get("last_processed_ids"):
        selected = set(st.session_state["last_processed_ids"])
        results = [item for item in workflow.db_manager.list_transactions() if item["transaction_id"] in selected]
        st.subheader("Processing results")
        st.dataframe(pd.DataFrame(display_transactions(results)), width="stretch", hide_index=True)


def analysis_page(workflow):
    st.title("AI Agent Analysis")
    transactions = workflow.db_manager.list_transactions()
    if not transactions:
        st.info("Transactions will appear here after CSV processing.")
        return
    st.dataframe(pd.DataFrame(display_transactions(transactions)), width="stretch", hide_index=True)
    with st.expander("Agent execution log"):
        st.dataframe(pd.DataFrame(workflow.db_manager.audit_history()["agent_logs"]), width="stretch", hide_index=True)


def approval_page(workflow):
    st.title("Approval Workbench")
    pending = workflow.db_manager.list_transactions(["PENDING_APPROVAL"])
    if not pending:
        st.info("There are no transactions waiting for approval.")
        return
    actor = st.text_input("Approver name", value="Finance Approver")
    for item in pending:
        label = f"{item['document_id']} | {item['risk_level']} risk | INR {item['validation']['total_amount']:,.2f}"
        with st.expander(label):
            st.write(item["recommendation"]["recommendation"])
            st.write(item["reasoning"]["explanation"])
            st.dataframe(pd.DataFrame(item["payload"]["lines"]), width="stretch", hide_index=True)
            approve, reject = st.columns(2)
            if approve.button("Approve", key=f"approve-{item['transaction_id']}", disabled=not item["validation"]["is_valid"]):
                try:
                    workflow.approve(item["transaction_id"], actor.strip() or "Finance Approver")
                    st.rerun()
                except (ValueError, sqlite3.Error) as exc:
                    st.error(str(exc))
            if reject.button("Reject", key=f"reject-{item['transaction_id']}"):
                try:
                    workflow.reject(item["transaction_id"], actor.strip() or "Finance Approver", "Rejected in approval workbench")
                    st.rerun()
                except (ValueError, sqlite3.Error) as exc:
                    st.error(str(exc))


def posting_page(workflow):
    st.title("Posting and Audit")
    approved = workflow.db_manager.list_transactions(["APPROVED"])
    if approved:
        st.subheader("Approved transactions")
        for item in approved:
            column, action = st.columns([5, 1])
            column.write(f"{item['document_id']} | INR {item['validation']['total_amount']:,.2f}")
            if action.button("Simulate posting", key=f"post-{item['transaction_id']}"):
                try:
                    workflow.post(item["transaction_id"])
                    st.rerun()
                except (ValueError, sqlite3.Error) as exc:
                    st.error(str(exc))
    st.subheader("Simulated postings")
    posted = workflow.db_manager.list_transactions(["POSTED"])
    posting_rows = [{"Document": item["document_id"], "Transaction ID": item["transaction_id"],
                     "Simulated SAP document": item["sap_document_number"], "Posting status": "SIMULATED", "Posted at": item["updated_at"]}
                    for item in posted]
    st.dataframe(pd.DataFrame(posting_rows), width="stretch", hide_index=True)
    st.caption("All posting references are local simulations. No real SAP system was contacted.")
    history = workflow.db_manager.audit_history()
    for title, key in (("Transaction history and agent decisions", "agent_logs"), ("Approval history", "approvals"), ("Posting history", "postings")):
        with st.expander(title, expanded=key == "agent_logs"):
            st.dataframe(pd.DataFrame(history[key]), width="stretch", hide_index=True)


def main():
    st.sidebar.title("Finance AI Agents")
    page = st.sidebar.radio("Workspace", ["Dashboard", "Journal Upload", "AI Agent Analysis", "Approval Workbench", "Posting and Audit"])
    try:
        workflow = get_workflow()
        pages = {"Dashboard": dashboard, "Journal Upload": upload_page, "AI Agent Analysis": analysis_page,
                 "Approval Workbench": approval_page, "Posting and Audit": posting_page}
        pages[page](workflow)
    except (sqlite3.Error, OSError, ValueError) as exc:
        st.error(f"Finance workflow could not start: {exc}")


if __name__ == "__main__":
    main()
