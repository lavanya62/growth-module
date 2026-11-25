"""Growth agent: turns the other agents' results into an action list."""
from agents.inventory_agent import analyze_inventory
from agents.sales_agent import analyze_sales, percent_change


def build_report(df, safety_days=7, cover_days=30):
    sales = analyze_sales(df)
    inventory = analyze_inventory(df, safety_days, cover_days)
    return {
        "sales": sales,
        "inventory": inventory,
        "actions": recommend(df, sales, inventory),
    }


def recommend(df, sales, inventory):
    actions = []

    for item in inventory:
        if item["status"] in ("Urgent", "Reorder"):
            actions.append(
                f"{item['status']}: order about {item['reorder_qty']} units of "
                f"{item['product']} ({item['days_left']} days of stock left, "
                f"supplier takes {item['lead_time_days']} days)."
            )

    change = sales["latest_change_percent"]
    if change is not None and change < 0:
        actions.append(
            f"Revenue fell {abs(change)}% in the latest month. Check pricing, "
            "stock-outs and promotions."
        )
    elif change is not None and change > 0:
        actions.append(
            f"Revenue rose {change}% in the latest month. Find what drove it "
            "before spending more."
        )

    months = sales["monthly"]
    if len(months) >= 2:
        units = df.pivot_table(index="product", columns=df["month"].astype(str),
                               values="units_sold", aggfunc="sum", fill_value=0)
        previous, latest = months[-2]["month"], months[-1]["month"]
        moves = []
        for product, row in units.iterrows():
            move = percent_change(row.get(previous, 0), row.get(latest, 0))
            if move is not None:
                moves.append((move, product))
        if moves:
            best, worst = max(moves), min(moves)
            if best[0] >= 10:
                actions.append(f"Promote {best[1]}: units sold up {best[0]}% month on month.")
            if worst[0] <= -10:
                actions.append(f"Review {worst[1]}: units sold down {abs(worst[0])}% month on month.")

    if sales["total_profit"] > 0:
        top = max(sales["products"], key=lambda p: p["profit"])
        actions.append(f"Protect {top['product']}, your biggest source of gross profit.")

    for item in inventory:
        if item["status"] == "Overstock":
            actions.append(
                f"Pause reordering {item['product']}: about {item['days_left']} days of stock. "
                "Consider a bundle or discount."
            )
        elif item["status"] == "No recent sales":
            actions.append(f"{item['product']} has no recent sales. Decide whether to keep it.")
    return actions
