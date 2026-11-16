from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "data" / "finance_knowledge_base.json"
DATABASE_PATH = Path(os.environ.get("FINANCE_DB_PATH", BASE_DIR / "finance_workflow.db"))
