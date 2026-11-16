# Architecture

```mermaid
flowchart LR
    CSV[CSV upload] --> Intake[Journal Intake Agent]
    Intake --> Validation[Financial Validation Agent]
    Validation --> Rules[Knowledge-Based Reasoning Agent]
    Rules --> Recommendation[Recommendation Agent]
    Recommendation --> DB[(SQLite audit database)]
    Recommendation --> Approval[Human approval workbench]
    Approval --> Posting[Approval and Posting Agent]
    Posting --> Simulated[SAP simulation only]
    Posting --> DB
    DB --> UI[Streamlit dashboard and audit views]
```

The `FinanceWorkflowOrchestrator` coordinates deterministic agent decisions. Finance rules and master data live in JSON. Guarded SQLite state transitions enforce that only valid, approved entries can be simulated for posting.
