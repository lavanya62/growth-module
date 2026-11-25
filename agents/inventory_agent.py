"""Inventory agent: how long stock will last and what to reorder."""
import math

DAYS_PER_MONTH = 30


def analyze_inventory(df, safety_days=7, cover_days=30, recent_months=3):
    """Estimate stock cover from average sales over the most recent months.

    Assumes each row holds a full month of sales, and that the 'stock' value
    in a product's newest row is its current stock.
    """
    latest_month = df["month"].max()
    window_start = latest_month - (recent_months - 1)
    items = []

    for product, rows in df.groupby("product"):
        rows = rows.sort_values("date")
        current = rows.iloc[-1]
        recent = rows[rows["month"] >= window_start]
        # A product launched inside the window is averaged over its own age.
        first_month = max(window_start, rows["month"].min())
        months = (latest_month - first_month).n + 1
        daily = float(recent["units_sold"].sum()) / (months * DAYS_PER_MONTH)

        stock = float(current["stock"])
        lead = float(current["lead_time_days"])
        reorder_point = daily * (lead + safety_days)
        target = daily * (lead + safety_days + cover_days)
        days_left = stock / daily if daily else None

        if daily == 0:
            status = "No recent sales"
        elif days_left <= lead:
            status = "Urgent"
        elif stock <= reorder_point:
            status = "Reorder"
        elif days_left > 90:
            status = "Overstock"
        else:
            status = "OK"

        reorder_qty = math.ceil(target - stock) if status in ("Urgent", "Reorder") else 0
        items.append({
            "product": product,
            "stock": int(stock),
            "daily_sales": round(daily, 2),
            "days_left": None if days_left is None else round(days_left, 1),
            "lead_time_days": int(lead),
            "status": status,
            "reorder_qty": max(reorder_qty, 0),
        })

    order = {"Urgent": 0, "Reorder": 1, "Overstock": 2, "No recent sales": 3, "OK": 4}
    return sorted(items, key=lambda i: (order[i["status"]], i["product"]))
