from collections import defaultdict
from math import sqrt
from statistics import pstdev


def build_reorder_plan(
    inventory: list[dict],
    demand_history: list[dict],
    suppliers: list[dict],
    service_level_z: float = 1.65,
) -> list[dict]:
    demand_by_product: dict[str, list[int]] = defaultdict(list)
    for row in demand_history:
        demand_by_product[row["product_id"]].append(int(row["demand"]))

    supplier_by_product = {}
    for supplier in sorted(suppliers, key=lambda row: (row["lead_time_days"], row["unit_cost"])):
        supplier_by_product.setdefault(supplier["product_id"], supplier)

    plan = []
    for row in inventory:
        product_id = row["product_id"]
        demand_values = demand_by_product.get(product_id, [0])
        supplier = supplier_by_product.get(product_id, {"lead_time_days": 7})
        lead_time_days = int(supplier["lead_time_days"])
        avg_monthly_demand = sum(demand_values) / len(demand_values)
        avg_daily_demand = avg_monthly_demand / 30
        demand_std = pstdev(demand_values) / 30 if len(demand_values) > 1 else 0
        safety_stock = round(service_level_z * demand_std * sqrt(lead_time_days))
        demand_during_lead_time = round(avg_daily_demand * lead_time_days)
        reorder_point = demand_during_lead_time + safety_stock
        available = int(row["on_hand"]) - int(row.get("reserved", 0))
        shortage = max(0, reorder_point - available)
        stockout_risk = "High" if available < demand_during_lead_time else "Medium" if available < reorder_point else "Low"
        overstock_risk = "High" if available > avg_monthly_demand * 1.8 else "Low"

        plan.append(
            {
                "warehouse_id": row["warehouse_id"],
                "product_id": product_id,
                "available_inventory": available,
                "lead_time_days": lead_time_days,
                "average_monthly_demand": round(avg_monthly_demand, 1),
                "safety_stock": safety_stock,
                "reorder_point": reorder_point,
                "recommended_reorder_quantity": shortage,
                "stockout_risk": stockout_risk,
                "overstock_risk": overstock_risk,
            }
        )
    return plan
