# Quick Start Guide

Get the Finance Workflow Automation dashboard running in 2 minutes!

## Prerequisites

- Python 3.11 or higher ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))

## Installation (2 minutes)

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/AutonomusJEvalidation-project.git
cd AutonomusJEvalidation-project
```

### 2. Create Virtual Environment
```bash
# macOS/Linux
python -m venv .venv && source .venv/bin/activate

# Windows
python -m venv .venv && .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run Application
```bash
streamlit run app.py
```

✅ **Done!** Open [http://localhost:8501](http://localhost:8501) in your browser.

## First Steps

1. **Upload Sample Data:**
   - Click "Journal Upload" in sidebar
   - Upload `data/sample_journal_entries.csv`
   - Click "Process Transactions"

2. **Review Results:**
   - Check "AI Agent Analysis" to see validation details
   - See which entries passed and which failed

3. **Try Approval:**
   - Go to "Approval Workbench"
   - Click "Approve" on a valid transaction
   - Go to "Posting and Audit" to see the simulated SAP reference

4. **Explore Dashboard:**
   - View transaction status and risk distribution
   - Review agent execution logs and audit history

## Key Features

| Page | Purpose |
|------|---------|
| **Dashboard** | Real-time transaction metrics and trends |
| **Journal Upload** | Submit CSV files for processing |
| **AI Agent Analysis** | Detailed validation and policy results |
| **Approval Workbench** | Human approval/rejection decisions |
| **Posting and Audit** | Simulated posting and complete audit trail |

## Sample Data

The included `data/sample_journal_entries.csv` contains:
- ✅ 4 valid journal entries ready for approval
- ❌ 6 invalid entries with various validation issues
- 🔍 Examples of duplicates, imbalances, missing data, and policy violations

## Troubleshooting

**Port 8501 already in use?**
```bash
streamlit run app.py --server.port 8502
```

**Missing dependencies?**
```bash
pip install --force-reinstall -r requirements.txt
```

**Want to reset?**
```bash
rm finance_workflow.db
streamlit run app.py
```

## Run Tests

```bash
python -m pytest -q
```

Expected: All 14 tests pass ✅

## Learn More

- 📖 [Full Setup Guide](SETUP.md)
- 🏗️ [Architecture Overview](docs/architecture.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)
- 📚 [Documentation](README.md)

## Support

Need help?
- Check [GitHub Issues](https://github.com/yourusername/AutonomusJEvalidation-project/issues)
- Review [SETUP.md](SETUP.md) for troubleshooting
- See [docs/](docs/) folder for detailed documentation

---

**Enjoy exploring the Finance Workflow Automation system!** 🚀
