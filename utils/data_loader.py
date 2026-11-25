"""Load and validate the business CSV."""
import pandas as pd

TEXT_COLUMNS = ["date", "product"]
NUMBER_COLUMNS = ["units_sold", "unit_price", "unit_cost", "stock", "lead_time_days"]


class DataError(ValueError):
    """Raised when the CSV cannot be used."""


def load_data(source):
    """Read a CSV (path or file object) and return a clean DataFrame."""
    try:
        df = pd.read_csv(source)
    except FileNotFoundError:
        raise DataError(f"Data file not found: {source}")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        raise DataError("The file is empty or is not a valid CSV.")

    df.columns = df.columns.str.strip().str.lower()
    missing = [c for c in TEXT_COLUMNS + NUMBER_COLUMNS if c not in df.columns]
    if missing:
        raise DataError("Missing columns: " + ", ".join(missing))
    if df.empty:
        raise DataError("The CSV has no data rows.")
    if df[TEXT_COLUMNS + NUMBER_COLUMNS].isna().any().any():
        raise DataError("Some required cells are blank.")

    try:
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    except ValueError:
        raise DataError("Dates must look like YYYY-MM-DD.")
    for column in NUMBER_COLUMNS:
        values = pd.to_numeric(df[column], errors="coerce")
        if values.isna().any() or (values < 0).any() or (values == float("inf")).any():
            raise DataError(f"Column '{column}' must contain numbers of 0 or more.")
        df[column] = values

    df["product"] = df["product"].astype(str).str.strip()
    df["month"] = df["date"].dt.to_period("M")
    if df.duplicated(["month", "product"]).any():
        raise DataError("Use only one row per product per month.")

    df["revenue"] = df["units_sold"] * df["unit_price"]
    df["profit"] = df["units_sold"] * (df["unit_price"] - df["unit_cost"])
    return df.sort_values(["date", "product"]).reset_index(drop=True)
