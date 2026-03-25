import pandas as pd
from pathlib import Path
from typing import List, Dict
from models import Period

# --------------------------------------------------
# Configuration
# --------------------------------------------------

CSV_PATH = Path("price_history.csv")

# --------------------------------------------------
# Load & clean price history
# --------------------------------------------------

def load_price_history() -> pd.DataFrame:
    """
    Load and normalize the price history CSV.
    """
    if not CSV_PATH.exists():
        return pd.DataFrame()
        
    df = pd.read_csv(CSV_PATH)

    df["app_id"] = pd.to_numeric(df["app_id"], errors="coerce")

    df["final_price"] = pd.to_numeric(df["final_price"], errors="coerce")
    df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.dropna(subset=["final_price", "date", "app_id"])

    return df


# --------------------------------------------------
# Filter by game
# --------------------------------------------------

def filter_game_by_id(df: pd.DataFrame, game_id: int) -> pd.DataFrame:
    """
    Filter price history for a single game.
    """
    if df.empty or "app_id" not in df.columns:
        return pd.DataFrame()

    return df[df["app_id"] == game_id]


# --------------------------------------------------
# Aggregate price trends
# --------------------------------------------------

def aggregate_prices(
    df: pd.DataFrame,
    period: Period
) -> List[Dict]:
    """
    Aggregate price data based on period.
    Returns a list of {date, final_price}.
    """

    if df.empty:
        return []

    # DAILY (raw history)
    if period == Period.daily:
        return (
            df.sort_values("date")[["date", "final_price"]]
            .to_dict(orient="records")
        )

    # MONTHLY (average per month)
    if period == Period.monthly:
        df["month"] = df["date"].dt.to_period("M")

        return (
            df.groupby("month")["final_price"]
            .mean()
            .reset_index()
            .assign(date=lambda x: x["month"].dt.to_timestamp())
            [["date", "final_price"]]
            .to_dict(orient="records")
        )

    # YEARLY (average per year)
    if period == Period.yearly:
        df["year"] = df["date"].dt.year

        return (
            df.groupby("year")["final_price"]
            .mean()
            .reset_index()
            .assign(date=lambda x: pd.to_datetime(x["year"], format="%Y"))
            [["date", "final_price"]]
            .to_dict(orient="records")
        )

    # Safety fallback (should never happen because Enum)
    return []
