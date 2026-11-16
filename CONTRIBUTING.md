# Contributing to Autonomous AI Agents for Enterprise Finance Workflow Automation

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful and constructive in all interactions. We're building a community where everyone feels welcome and valued.

## How to Contribute

### 1. Reporting Bugs

Found a bug? Please create an issue with:

- **Title:** Brief description of the issue
- **Description:** Clear explanation of what's broken
- **Reproduction Steps:**
  ```
  1. Clone the repository
  2. Create virtual environment
  3. Run `streamlit run app.py`
  4. Navigate to [specific page]
  5. [Specific action that causes the bug]
  ```
- **Expected Behavior:** What should happen
- **Actual Behavior:** What actually happens
- **Environment:**
  - OS (Windows/macOS/Linux)
  - Python version
  - Streamlit version
  - Any relevant error messages

### 2. Suggesting Features or Enhancements

Have an idea? Open an issue with:

- **Title:** Feature request: [brief description]
- **Description:** Detailed explanation of the feature
- **Use Case:** Why is this useful?
- **Possible Implementation:** Any ideas on how to implement it
- **Related Issues:** Link any related issues or discussions

### 3. Submitting Code Changes

#### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/AutonomusJEvalidation-project.git
cd AutonomusJEvalidation-project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode
python -m pip install -r requirements.txt
```

#### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/description-of-feature
   ```

2. **Make your changes:**
   - Follow the existing code style (PEP 8)
   - Use type hints in functions
   - Add docstrings to classes and public methods
   - Keep functions focused and readable

3. **Add tests:**
   ```bash
   # Add tests to tests/ directory
   pytest tests/  # Verify tests pass
   ```

4. **Update documentation:**
   - Update README.md if adding new features
   - Update docs/project_documentation.md if changing architecture
   - Add docstrings to new functions and classes

5. **Verify your changes:**
   ```bash
   # Run all tests
   python -m pytest -q
   
   # Run the application
   streamlit run app.py
   ```

#### Submitting a Pull Request

1. **Push to your fork:**
   ```bash
   git add .
   git commit -m "feat: add feature description"
   git push origin feature/description-of-feature
   ```

2. **Open a Pull Request:**
   - **Title:** Clear, descriptive title
   - **Description:** Include:
     - What this PR does
     - Why it's needed
     - Any related issues (use `Closes #123`)
     - Test results
   
   **Example PR Description:**
   ```markdown
   ## Description
   Adds support for bulk journal upload and batch processing.
   
   ## Related Issue
   Closes #42
   
   ## Type of Change
   - [x] Bug fix
   - [x] New feature
   - [ ] Breaking change
   
   ## Testing
   - [x] Unit tests added
   - [x] Integration tests passed
   - [x] Manual testing completed
   
   ## Checklist
   - [x] My code follows the project's code style
   - [x] I've added tests for new functionality
   - [x] All tests pass
   - [x] Documentation updated
   ```

## Architecture and Design Patterns

### Agent-Based Architecture

The project uses five independent agents coordinated by `FinanceWorkflowOrchestrator`:

- **Intake Agent:** Stateless, transforms CSV to documents
- **Validation Agent:** Deterministic checks against rules
- **Reasoning Agent:** Maps errors to policy rules
- **Recommendation Agent:** Produces actionable guidance
- **Approval/Posting Agent:** Manages state transitions in SQLite

When adding features:
- Keep agents focused on a single responsibility
- Use `knowledge_base/knowledge_service.py` for business rules (don't hardcode)
- Add database persistence through `database/db_manager.py`

### Adding New Validation Rules

1. **Define the rule in `data/finance_knowledge_base.json`:**
   ```json
   {
     "id": "YOUR_RULE_ID",
     "name": "Human readable name",
     "error_codes": ["ERROR_CODE"],
     "explanation": "Why this rule matters",
     "action": "What the user should do"
   }
   ```

2. **Implement the check in `validation_agent.py`:**
   ```python
   if condition_not_met:
       errors.append(self._error("ERROR_CODE", "message"))
   ```

3. **Add test in `tests/test_validation.py`:**
   ```python
   def test_your_new_validation():
       result = validate_lines([...])
       assert "ERROR_CODE" in {error["code"] for error in result["errors"]}
   ```

## Code Style Guide

### Python Style

- **Format:** PEP 8
- **Line Length:** 120 characters
- **Type Hints:** Required for function signatures
- **Docstrings:** Google style

**Example:**
```python
def validate_amount(amount: float, max_value: float) -> bool:
    """Validate if amount is within acceptable range.
    
    Args:
        amount: The amount to validate
        max_value: Maximum allowed value
        
    Returns:
        True if valid, False otherwise
    """
    return 0 <= amount <= max_value
```

### Test Style

- **Framework:** pytest
- **Naming:** `test_<function>_<scenario>`
- **Coverage:** Aim for >80%
- **Fixtures:** Use pytest fixtures for setup

**Example:**
```python
def test_validation_fails_with_negative_amount():
    lines = [{"debit": -100, "credit": 0, ...}]
    result = validate_lines(lines)
    assert "NEGATIVE_AMOUNT" in {e["code"] for e in result["errors"]}
```

## Testing Requirements

- All new features must include tests
- Existing tests must continue to pass
- Run tests locally before submitting PR:
  ```bash
  python -m pytest -q
  ```

## Documentation

- Update README.md for user-facing changes
- Update docs/project_documentation.md for architecture changes
- Add docstrings to all new functions and classes
- Use clear, concise language

## Performance Considerations

- Minimize database transactions in loops
- Use batch operations where possible
- Profile memory usage for large datasets
- Consider n+1 query problems in workflows

## Questions or Need Help?

- Open a discussion on GitHub
- Check existing issues for similar questions
- Review docs/ folder for detailed documentation

## Recognition

Contributors will be recognized in:
- Project README (Contributors section)
- Release notes for significant contributions
- GitHub contributors page

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make this project better! 🎉
