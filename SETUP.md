# Setup Guide

Complete guide for setting up the Autonomous AI Agents for Enterprise Finance Workflow Automation project.

## Prerequisites

- **Python:** 3.11 or higher
  - [Download Python](https://www.python.org/downloads/)
  - Verify installation: `python --version`
- **Git:** For cloning and version control
  - [Download Git](https://git-scm.com/downloads)
- **pip:** Comes with Python 3.4+
  - Verify: `pip --version`

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AutonomusJEvalidation-project.git
cd AutonomusJEvalidation-project
```

### 2. Create Virtual Environment

#### On macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### On Windows (Command Prompt):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Verify activation:** Your terminal should show `(.venv)` at the beginning of the prompt.

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:** All packages should install successfully without errors.

### 5. Verify Installation

```bash
# Test imports
python -c "import streamlit, pandas, pytest; print('All dependencies installed!')"

# Verify Python version
python --version  # Should be 3.11 or higher
```

### 6. Run Tests

```bash
python -m pytest -q
```

**Expected output:** All 14 tests should pass.

```
..............                                                           [100%]
14 passed in 0.99s
```

### 7. Start the Application

```bash
streamlit run app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Open your browser to [http://localhost:8501](http://localhost:8501)

## Troubleshooting

### Python Version Issues

**Problem:** `python` command not found  
**Solution:** 
- On macOS/Linux, try `python3`
- On Windows, ensure Python is in PATH or use full path

**Problem:** Python version is 3.10 or lower  
**Solution:** Install Python 3.11+

### Virtual Environment Issues

**Problem:** Virtual environment not activating  
**Solution:**
```bash
# Recreate the virtual environment
rm -rf .venv  # or rmdir /s .venv on Windows
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### Dependency Installation Issues

**Problem:** `pip install -r requirements.txt` fails  
**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Try installing again with verbose output
pip install -r requirements.txt -v
```

**Problem:** ModuleNotFoundError after installation  
**Solution:**
- Verify virtual environment is activated
- Try: `pip install --force-reinstall -r requirements.txt`

### Application Won't Start

**Problem:** `streamlit run app.py` fails  
**Solution:**
```bash
# Verify Streamlit is installed
pip list | grep streamlit  # or findstr streamlit on Windows

# Reinstall Streamlit
pip install --force-reinstall streamlit
```

**Problem:** Port 8501 already in use  
**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Database Issues

**Problem:** Database errors on startup  
**Solution:**
```bash
# Remove and let app recreate it
rm finance_workflow.db
streamlit run app.py
```

## Development Setup

### Additional Tools (Optional)

```bash
# Code formatting
pip install black flake8 isort

# Type checking
pip install mypy

# Enhanced testing
pip install pytest-cov pytest-xdist
```

### IDE Setup

#### VS Code
1. Install [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
2. Select interpreter: `.venv`
3. Install [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)

#### PyCharm
1. Go to: File → Settings → Project → Python Interpreter
2. Click "Add" and select ".venv" folder
3. Apply changes

## Environment Configuration

### Custom Database Location

```bash
# Set environment variable (macOS/Linux)
export FINANCE_DB_PATH=/path/to/custom/database.db
streamlit run app.py

# Set environment variable (Windows PowerShell)
$env:FINANCE_DB_PATH = "C:\path\to\database.db"
streamlit run app.py

# Set environment variable (Windows Command Prompt)
set FINANCE_DB_PATH=C:\path\to\database.db
streamlit run app.py
```

## Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (no errors)
- [ ] All 14 tests pass
- [ ] Application starts without errors
- [ ] Streamlit dashboard loads at http://localhost:8501
- [ ] Sample CSV can be uploaded and processed

## Next Steps

1. **Explore the sample data:**
   - Go to "Journal Upload" page
   - Upload `data/sample_journal_entries.csv`

2. **Review the documentation:**
   - Read [docs/architecture.md](docs/architecture.md)
   - Review [docs/project_documentation.md](docs/project_documentation.md)

3. **Understand the workflow:**
   - Navigate through each dashboard page
   - Try approving/rejecting transactions
   - Generate simulated postings

4. **Run the tests:**
   ```bash
   python -m pytest -v  # Verbose output
   python -m pytest tests/test_validation.py  # Specific test file
   ```

## Getting Help

- **Documentation:** See [README.md](README.md)
- **Issues:** Check [GitHub Issues](https://github.com/yourusername/AutonomusJEvalidation-project/issues)
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)

## Uninstalling

To completely remove the project:

```bash
# Remove virtual environment
rm -rf .venv  # macOS/Linux
rmdir /s .venv  # Windows

# Remove project directory
cd ..
rm -rf AutonomusJEvalidation-project  # macOS/Linux
rmdir /s AutonomusJEvalidation-project  # Windows
```

---

**Last Updated:** November 2026
