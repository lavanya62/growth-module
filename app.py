"""Growth module. Run:  python app.py  (or: python app.py path/to/file.csv)"""
import json
import os
import sys
from pathlib import Path

from dotenv import dotenv_values

from agents.growth_agent import build_report
from utils.data_loader import DataError, load_data

BASE_DIR = Path(__file__).resolve().parent


def run(csv_path=None):
    """Analyze a CSV and return the report as a dictionary.

    Raises DataError for bad CSV data and ValueError for bad settings.
    """
    # Read settings without changing the main project's environment variables.
    settings = {**dotenv_values(BASE_DIR / ".env"), **os.environ}
    path = csv_path or BASE_DIR / settings.get("DATA_FILE", "data/business.csv")
    return build_report(
        load_data(path),
        safety_days=int(settings.get("SAFETY_DAYS", 7)),
        cover_days=int(settings.get("COVER_DAYS", 30)),
    )


if __name__ == "__main__":
    try:
        report = run(sys.argv[1] if len(sys.argv) > 1 else None)
    except (DataError, ValueError) as exc:
        sys.exit(f"Error: {exc}")
    print(json.dumps(report, indent=2))
