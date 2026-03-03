from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DB_URL")
BASE_DIR = Path(__file__).parent


DIRS = {
    "raw": BASE_DIR / "data" / "raw",
    "processed": BASE_DIR / "data" / "processed",
}


def init_dirs():
    for path in DIRS.values():
        path.mkdir(parents=True, exist_ok=True)
