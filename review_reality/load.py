"""Read the raw Datafiniti CSV files and give them the same simple column names.

The three files have slightly different columns. We keep only the columns
that every file has (and that we need), and rename them to short names.
No values are changed here; cleaning happens in clean.py.
"""
import pandas as pd

from review_reality.paths import RAW_DIR, RAW_FILES

# raw column name -> our column name
COLUMNS = {
    "name": "listing_name",
    "asins": "asins",
    "reviews.date": "review_date",
    "reviews.rating": "rating",
    "reviews.title": "title",
    "reviews.text": "text",
    "reviews.username": "username",
    "reviews.doRecommend": "recommends",
    "reviews.numHelpful": "helpful_votes",
    "reviews.sourceURLs": "source_url",
}


def load_raw_file(file_key, raw_dir=RAW_DIR):
    """Load one raw CSV, keep the shared columns, and note which file it came from."""
    path = raw_dir / RAW_FILES[file_key]
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Download the Kaggle zip and unzip it into {raw_dir} (see docs/DATASET.md)."
        )
    df = pd.read_csv(path, usecols=list(COLUMNS), dtype=str, keep_default_na=True)
    df = df.rename(columns=COLUMNS)
    df["source_file"] = file_key
    return df


def load_all_raw(raw_dir=RAW_DIR):
    """Load all three raw files and stack them into one table (rows are not de-duplicated yet)."""
    frames = [load_raw_file(key, raw_dir) for key in RAW_FILES]
    return pd.concat(frames, ignore_index=True)
