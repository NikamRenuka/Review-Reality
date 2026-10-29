"""All file locations in one place, so no other file hard-codes a path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "datafiniti"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = PROCESSED_DIR / "reviews.db"
SQL_DIR = ROOT / "sql"
DOCS_DIR = ROOT / "docs"

# The three CSV files inside the Kaggle zip (oldest first).
RAW_FILES = {
    "2018_04": "1429_1.csv",
    "2018_09": "Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv",
    "2019_05": "Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products_May19.csv",
}
