import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

WAREHOUSES = [
    {"warehouse_id": "A", "warehouse_name": "Warehouse A", "region": "Brewery North", "storage_capacity": 1000},
    {"warehouse_id": "B", "warehouse_name": "Warehouse B", "region": "Brewery South", "storage_capacity": 4000},
]

CUSTOMERS = [
    {"customer_id": "BAR_1", "customer_name": "Bar 1", "region": "Bar 1"},
    {"customer_id": "BAR_2", "customer_name": "Bar 2", "region": "Bar 2"},
    {"customer_id": "BAR_3", "customer_name": "Bar 3", "region": "Bar 3"},
    {"customer_id": "BAR_4", "customer_name": "Bar 4", "region": "Bar 4"},
    {"customer_id": "BAR_5", "customer_name": "Bar 5", "region": "Bar 5"},
]

DEMAND = {"BAR_1": 500, "BAR_2": 900, "BAR_3": 1800, "BAR_4": 200, "BAR_5": 700}
SUPPLY = {"A": 1000, "B": 4000}
COSTS = {
    "A": {"BAR_1": 2, "BAR_2": 4, "BAR_3": 5, "BAR_4": 2, "BAR_5": 1},
    "B": {"BAR_1": 3, "BAR_2": 1, "BAR_3": 3, "BAR_4": 2, "BAR_5": 3},
}


def write_csv(filename: str, columns: list[str], rows: list[dict]) -> None:
    pd.DataFrame(rows, columns=columns).to_csv(RAW_DIR / filename, index=False)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    products = [
        {
            "product_id": "BEER_CRATE",
            "product_name": "Beer Crate",
            "category": "Beverage",
            "unit_price": 20,
        }
    ]
    suppliers = [
        {
            "supplier_id": "BREWERY_SUPPLIER",
            "supplier_name": "Boutique Brewery",
            "product_id": "BEER_CRATE",
            "unit_cost": 11,
            "lead_time_days": 2,
            "reliability_score": 96,
            "capacity": 5000,
            "quality_score": 98,
            "past_delay_rate": 2,
        }
    ]
    inventory = [
        {"warehouse_id": warehouse_id, "product_id": "BEER_CRATE", "on_hand": quantity, "reserved": 0}
        for warehouse_id, quantity in SUPPLY.items()
    ]
    demand_history = []
    for period in ("2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"):
        for customer in CUSTOMERS:
            demand_history.append(
                {
                    "product_id": "BEER_CRATE",
                    "region": customer["region"],
                    "period": period,
                    "demand": DEMAND[customer["customer_id"]],
                }
            )
    shipping_costs = []
    for warehouse_id, customer_costs in COSTS.items():
        for customer_id, cost in customer_costs.items():
            shipping_costs.append(
                {
                    "warehouse_id": warehouse_id,
                    "customer_id": customer_id,
                    "product_id": "BEER_CRATE",
                    "shipping_cost": cost,
                    "distance_km": cost * 100,
                    "delivery_time_days": max(1, cost),
                }
            )

    write_csv("products.csv", ["product_id", "product_name", "category", "unit_price"], products)
    write_csv(
        "suppliers.csv",
        [
            "supplier_id",
            "supplier_name",
            "product_id",
            "unit_cost",
            "lead_time_days",
            "reliability_score",
            "capacity",
            "quality_score",
            "past_delay_rate",
        ],
        suppliers,
    )
    write_csv("warehouses.csv", ["warehouse_id", "warehouse_name", "region", "storage_capacity"], WAREHOUSES)
    write_csv("customers.csv", ["customer_id", "customer_name", "region"], CUSTOMERS)
    write_csv("inventory.csv", ["warehouse_id", "product_id", "on_hand", "reserved"], inventory)
    write_csv("demand_history.csv", ["product_id", "region", "period", "demand"], demand_history)
    write_csv(
        "shipping_costs.csv",
        ["warehouse_id", "customer_id", "product_id", "shipping_cost", "distance_km", "delivery_time_days"],
        shipping_costs,
    )

    metadata = {
        "source": "COIN-OR PuLP Beer Distribution",
        "repository": "https://coin-or.github.io/pulp/CaseStudies/a_transportation_problem.html",
        "notes": [
            "This is an online transportation-problem benchmark, not a large real transaction dataset.",
            "Warehouse supply, bar demand, and route costs come from the PuLP case study.",
            "The instance is feasible because total warehouse supply is 5000 and total bar demand is 4100.",
        ],
        "row_counts": {
            "products": len(products),
            "suppliers": len(suppliers),
            "warehouses": len(WAREHOUSES),
            "customers": len(CUSTOMERS),
            "inventory": len(inventory),
            "demand_history": len(demand_history),
            "shipping_costs": len(shipping_costs),
        },
    }
    (RAW_DIR / "pulp_beer_distribution_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata["row_counts"], indent=2))


if __name__ == "__main__":
    main()
