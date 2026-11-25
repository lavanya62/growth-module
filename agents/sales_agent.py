"""Sales agent: revenue, profit and monthly trend."""
import pandas as pd


def percent_change(old, new):
    """Return the % change, or None when there is no base to compare with."""
    if old == 0:
        return None
    return round((new - old) / old * 100, 1)


def analyze_sales(df):
    revenue = float(df["revenue"].sum())
    profit = float(df["profit"].sum())

    monthly = df.groupby("month")[["revenue", "profit"]].sum().sort_index()
    # Count calendar months with no rows as zero sales.
    full_range = pd.period_range(monthly.index.min(), monthly.index.max(), freq="M")
    monthly = monthly.reindex(full_range, fill_value=0)

    latest_change = None
    if len(monthly) >= 2:
        latest_change = percent_change(monthly["revenue"].iloc[-2], monthly["revenue"].iloc[-1])

    products = df.groupby("product")[["units_sold", "revenue", "profit"]].sum()
    products = products.sort_values("revenue", ascending=False)

    return {
        "total_revenue": round(revenue, 2),
        "total_profit": round(profit, 2),
        "margin_percent": round(profit / revenue * 100, 1) if revenue else 0.0,
        "latest_change_percent": latest_change,
        "monthly": [
            {"month": str(m), "revenue": float(r.revenue), "profit": float(r.profit)}
            for m, r in monthly.iterrows()
        ],
        "products": [
            {
                "product": name,
                "units": int(r.units_sold),
                "revenue": float(r.revenue),
                "profit": float(r.profit),
                "margin_percent": round(r.profit / r.revenue * 100, 1) if r.revenue else 0.0,
            }
            for name, r in products.iterrows()
        ],
    }
