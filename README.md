# Autonomous AI Agents for Enterprise Finance Workflow Automation

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#tests)

## Introduction

A local academic demonstration of rule-based journal processing using Streamlit, Pandas, SQLite, and a JSON finance knowledge base. This project showcases a multi-agent workflow for enterprise finance automation with deterministic policy-based reasoning. No API key, paid service, or SAP connection is required. SAP document references are simulated.

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/yourusername/AutonomusJEvalidation-project.git
cd AutonomusJEvalidation-project
```

### Setup and Run

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application will open at [http://localhost:8501](http://localhost:8501)

## Problem and Objectives

Finance teams need to validate journal data, enforce policy, identify anomalies, obtain approval, and retain an audit trail. This project automates those checks on uploaded CSV journal lines while leaving the approval decision with a human.

Objectives: check balances and master data, explain policy outcomes, detect duplicates and amount anomalies, recommend corrective action, require approval, and demonstrate guarded simulated posting.

## Technology Stack

Python 3.11+, Streamlit, Pandas, SQLite, JSON, and Pytest.

## Architecture and Agents

- **Journal Intake Agent:** reads CSV, groups lines into documents, and assigns transaction IDs.
- **Financial Validation Agent:** checks required fields, balance, GL/cost-centre/company masters, duplicates, amount integrity, and cross-company accounts.
- **Knowledge-Based Reasoning Agent:** maps validation results to JSON rule explanations.
- **Recommendation Agent:** assigns LOW, MEDIUM, or HIGH risk and recommends correction or approval.
- **Approval and Posting Agent:** records a human decision and allows simulated posting only after approval.

`FinanceWorkflowOrchestrator` coordinates the five classes. Rules and master data are in `data/finance_knowledge_base.json`; add rules there without changing workflow code. See [docs/architecture.md](docs/architecture.md) and [docs/project_documentation.md](docs/project_documentation.md).

## Workflow

CSV upload -> intake -> financial validation -> policy reasoning -> recommendation -> human approval/rejection -> simulated posting -> SQLite audit history. Invalid entries stop at `VALIDATION_FAILED`; valid entries enter `PENDING_APPROVAL`. Only valid and approved entries can become `POSTED`.

## Installation

From the project directory, create and activate a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows Command Prompt: .venv\Scripts\activate.bat
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Python 3.11+ is required. If a Python release has no compatible Pandas/Streamlit wheels yet, use Python 3.11-3.13 and recreate the environment.

## Run

From this directory:

```bash
streamlit run app.py
```

SQLite is created automatically as `finance_workflow.db`. Set `FINANCE_DB_PATH` to select another database file. Stop the application before removing the database to reset a demonstration.

## Tests

```bash
python -m pytest -q
```

Tests cover validation, policy mapping, approval/rejection, posting guards, and successful simulated posting.

## Sample Demonstration

Upload `data/sample_journal_entries.csv` on Journal Upload. It contains balanced and unbalanced entries, invalid GL and cost-centre values, missing company data, a high-value journal, cross-company entries, duplicate content, negative amounts, and valid journals. Approve one valid item in the Approval Workbench, reject another, then view the simulated reference and audit events on Posting and Audit.

## Sample Screenshots

No screenshots are committed. Capture the dashboard, agent analysis, approval workbench, and posting/audit views from the running application for assignment submission.

## Limitations and Future Enhancements

This is not an accounting system of record. Master data is illustrative; authentication, role-based approval limits, multi-user concurrency, currency conversion, and real SAP integration are out of scope. Risk is deterministic and rule-based, not a trained machine-learning model. Future work could add richer approval roles, policy administration, and audit exports.

## Project Structure

```
AutonomusJEvalidation-project/
├── agents/                          # Multi-agent architecture
│   ├── intake_agent.py             # CSV intake and document grouping
│   ├── validation_agent.py         # Financial validation checks
│   ├── reasoning_agent.py          # Policy-based reasoning
│   ├── recommendation_agent.py     # Risk assessment and recommendations
│   └── approval_posting_agent.py   # Approval and simulated posting
├── data/
│   ├── sample_journal_entries.csv  # Sample test data (10 documents)
│   └── finance_knowledge_base.json # Finance rules and master data
├── database/
│   └── db_manager.py               # SQLite persistence layer
├── knowledge_base/
│   └── knowledge_service.py        # Rule loading and policy evaluation
├── workflow/
│   └── orchestrator.py             # Workflow coordination
├── tests/                           # Unit and integration tests
│   ├── test_validation.py
│   ├── test_reasoning.py
│   └── test_workflow.py
├── docs/                            # Architecture and design documentation
│   ├── architecture.md
│   └── project_documentation.md
├── app.py                           # Streamlit dashboard
├── config.py                        # Configuration
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Development

### Requirements

- **Python:** 3.11 or higher
- **Dependencies:** Listed in `requirements.txt`
  - Streamlit 1.40+
  - Pandas 2.2+
  - Pytest 8.0+

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/AutonomusJEvalidation-project.git
   cd AutonomusJEvalidation-project
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   
   # On Windows PowerShell:
   .venv\Scripts\Activate.ps1
   
   # On Windows Command Prompt:
   .venv\Scripts\activate.bat
   
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

### Running Tests

```bash
# Run all tests
python -m pytest -q

# Run specific test file
python -m pytest tests/test_validation.py -v

# Run with coverage
python -m pytest --cov=agents --cov=database --cov=workflow
```

### Running the Application

```bash
streamlit run app.py
```

Access the dashboard at `http://localhost:8501`

### Database Management

- SQLite database is automatically created as `finance_workflow.db` on first run
- To reset the application state:
  ```bash
  rm finance_workflow.db
  ```
- To use a custom database location:
  ```bash
  export FINANCE_DB_PATH=/path/to/custom.db
  streamlit run app.py
  ```

## Contributing

We welcome contributions! Here's how to get started:

### Fork and Branch

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/AutonomusJEvalidation-project.git
   cd AutonomusJEvalidation-project
   ```
3. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Making Changes

1. **Follow the project structure** - add agent logic in `agents/`, tests in `tests/`
2. **Update finance rules** in `data/finance_knowledge_base.json` rather than hardcoding business logic
3. **Write tests** for new functionality before submitting
4. **Verify all tests pass:**
   ```bash
   python -m pytest -q
   ```

### Submitting Changes

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add descriptive commit message"
   ```
2. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
3. **Submit a Pull Request** on GitHub with:
   - Clear description of changes
   - Motivation and context
   - Test results
   - Any breaking changes noted

### Code Style

- Follow PEP 8 conventions
- Use type hints in function signatures
- Include docstrings for classes and public methods
- Maintain consistent formatting (the project uses 4-space indentation)

## Issues and Support

### Reporting Issues

If you find a bug or have a suggestion:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Python version and OS
   - Relevant error messages or logs

### Getting Help

- Review the [documentation](docs/)
- Check the [sample demonstration](#sample-demonstration) section
- Examine test cases in `tests/` for usage examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this project in academic work, please cite it as:

```bibtex
@software{autonomous_je_validation,
  title={Autonomous AI Agents for Enterprise Finance Workflow Automation Using Knowledge-Based Reasoning},
  author={Your Name},
  year={2026},
  url={https://github.com/yourusername/AutonomusJEvalidation-project}
}
```

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the dashboard
- Uses [Pandas](https://pandas.pydata.org/) for data processing
- SQLite for local database persistence
- [Pytest](https://pytest.org/) for testing

---

**Last Updated:** November 2026  
**Project Status:** Active Development
