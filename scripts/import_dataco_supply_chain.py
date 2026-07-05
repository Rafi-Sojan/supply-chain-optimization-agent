import json
import re
from math import asin, ceil, cos, radians, sin, sqrt
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DATASET_SLUG = "shashwatwork/dataco-smart-supply-chain-for-big-data-analysis"
TOP_PRODUCTS = 12
TOP_CUSTOMERS = 40


def _safe_id(prefix: str, value: object) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", str(value)).strip("_").upper()
    return f"{prefix}_{text}" if text else prefix


def _download_dataset() -> Path:
    cache_root = (
        Path.home()
        / ".cache"
        / "kagglehub"
        / "datasets"
        / "shashwatwork"
        / "dataco-smart-supply-chain-for-big-data-analysis"
        / "versions"
    )
    cached_versions = sorted(cache_root.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True) if cache_root.exists() else []
    for cached in cached_versions:
        if (cached / "DataCoSupplyChainDataset.csv").exists():
            return cached

    try:
        import kagglehub
    except ImportError as exc:
        raise RuntimeError("Install kagglehub first: python -m pip install kagglehub") from exc
    return Path(kagglehub.dataset_download(DATASET_SLUG))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    a_lat, a_lon, b_lat, b_lon = map(radians, (lat1, lon1, lat2, lon2))
    dlat = b_lat - a_lat
    dlon = b_lon - a_lon
    value = sin(dlat / 2) ** 2 + cos(a_lat) * cos(b_lat) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(value))


def _write_csv(filename: str, columns: list[str], rows: list[dict]) -> None:
    pd.DataFrame(rows, columns=columns).to_csv(RAW_DIR / filename, index=False)


def _load_dataco_csv(dataset_dir: Path) -> pd.DataFrame:
    path = dataset_dir / "DataCoSupplyChainDataset.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing DataCoSupplyChainDataset.csv in {dataset_dir}")
    df = pd.read_csv(path, encoding="latin1")
    df["order_month"] = pd.to_datetime(df["order date (DateOrders)"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    df = df.dropna(subset=["Product Card Id", "Customer Id", "Market", "order_month"])
    df["product_id"] = df["Product Card Id"].map(lambda value: _safe_id("PROD", int(value)))
    df["customer_id"] = df["Customer Id"].map(lambda value: _safe_id("CUST", int(value)))
    df["warehouse_id"] = df["Market"].map(lambda value: _safe_id("WH", value))
    df["customer_region"] = df["customer_id"].map(lambda value: f"{value} - DataCo Customer")
    return df


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dataset_dir = _download_dataset()
    df = _load_dataco_csv(dataset_dir)

    top_products = (
        df.groupby("product_id")["Order Item Quantity"].sum().nlargest(TOP_PRODUCTS).index
    )
    product_df = df[df["product_id"].isin(top_products)].copy()
    top_customers = (
        product_df.groupby("customer_id")["Order Item Quantity"].sum().nlargest(TOP_CUSTOMERS).index
    )
    working = product_df[product_df["customer_id"].isin(top_customers)].copy()

    products = []
    for product_id, group in working.groupby("product_id"):
        first = group.iloc[0]
        products.append(
            {
                "product_id": product_id,
                "product_name": first["Product Name"],
                "category": first["Category Name"],
                "unit_price": round(float(group["Product Price"].median()), 2),
            }
        )
    products = sorted(products, key=lambda row: row["product_id"])

    product_price = {row["product_id"]: float(row["unit_price"]) for row in products}
    suppliers = []
    for row in products:
        product_rows = working[working["product_id"] == row["product_id"]]
        late_rate = float(product_rows["Late_delivery_risk"].mean() * 100)
        avg_days = float(product_rows["Days for shipment (scheduled)"].mean())
        total_quantity = int(product_rows["Order Item Quantity"].sum())
        suppliers.append(
            {
                "supplier_id": f"SUP_{row['product_id']}",
                "supplier_name": f"DataCo Supplier - {row['category']}",
                "product_id": row["product_id"],
                "unit_cost": round(row["unit_price"] * 0.62, 2),
                "lead_time_days": max(1, round(avg_days)),
                "reliability_score": round(max(1, 100 - late_rate), 1),
                "capacity": max(100, ceil(total_quantity * 1.4)),
                "quality_score": 90,
                "past_delay_rate": round(late_rate, 1),
            }
        )

    warehouses = []
    warehouse_coords = {}
    for warehouse_id, group in working.groupby("warehouse_id"):
        market = str(group.iloc[0]["Market"])
        lat = float(group["Latitude"].mean()) if group["Latitude"].notna().any() else 0.0
        lon = float(group["Longitude"].mean()) if group["Longitude"].notna().any() else 0.0
        warehouse_coords[warehouse_id] = (lat, lon)
        warehouses.append(
            {
                "warehouse_id": warehouse_id,
                "warehouse_name": f"{market} Distribution Hub",
                "region": market,
                "storage_capacity": max(1000, ceil(group["Order Item Quantity"].sum() * 1.5)),
            }
        )
    warehouses = sorted(warehouses, key=lambda row: row["warehouse_id"])

    customers = []
    customer_coords = {}
    for customer_id, group in working.groupby("customer_id"):
        first = group.iloc[0]
        first_name = str(first.get("Customer Fname", "")).strip()
        last_name = str(first.get("Customer Lname", "")).strip()
        display_name = f"{first_name} {last_name}".strip() or customer_id
        region = str(first["customer_region"])
        lat = float(group["Latitude"].mean()) if group["Latitude"].notna().any() else 0.0
        lon = float(group["Longitude"].mean()) if group["Longitude"].notna().any() else 0.0
        customer_coords[customer_id] = (lat, lon)
        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": display_name,
                "region": region,
            }
        )
    customers = sorted(customers, key=lambda row: row["customer_id"])

    demand_rows = (
        working.groupby(["product_id", "customer_region", "order_month"], as_index=False)["Order Item Quantity"]
        .sum()
        .rename(columns={"Order Item Quantity": "demand"})
    )
    demand_history = [
        {
            "product_id": row["product_id"],
            "region": row["customer_region"],
            "period": row["order_month"].strftime("%Y-%m-%d"),
            "demand": int(row["demand"]),
        }
        for _, row in demand_rows.iterrows()
        if int(row["demand"]) > 0
    ]

    latest_demand = pd.DataFrame(demand_history)
    latest_period = latest_demand["period"].max()
    latest_demand = (
        latest_demand.sort_values("period")
        .groupby(["product_id", "region"], as_index=False)
        .tail(1)
    )
    latest_by_product = latest_demand.groupby("product_id")["demand"].sum().to_dict()
    historical_share = (
        working.groupby(["warehouse_id", "product_id"])["Order Item Quantity"].sum()
        / working.groupby("product_id")["Order Item Quantity"].sum()
    ).to_dict()

    inventory = []
    for warehouse in warehouses:
        for product in products:
            product_id = product["product_id"]
            product_need = max(1, int(latest_by_product.get(product_id, 0)))
            share = float(historical_share.get((warehouse["warehouse_id"], product_id), 0.0))
            quantity = ceil(product_need * 1.35 * max(share, 0.08))
            inventory.append(
                {
                    "warehouse_id": warehouse["warehouse_id"],
                    "product_id": product_id,
                    "on_hand": max(5, quantity),
                    "reserved": 0,
                }
            )

    shipping_costs = []
    road_edges = []
    for warehouse in warehouses:
        wh_id = warehouse["warehouse_id"]
        wh_lat, wh_lon = warehouse_coords[wh_id]
        for customer in customers:
            cust_id = customer["customer_id"]
            cust_lat, cust_lon = customer_coords[cust_id]
            distance = max(10.0, _haversine_km(wh_lat, wh_lon, cust_lat, cust_lon))
            delivery_days = max(1, ceil(distance / 1200))
            route_cost = round(distance * 0.04 + delivery_days * 2, 2)
            road_edges.append(
                {
                    "from_node": wh_id,
                    "to_node": cust_id,
                    "distance_km": round(distance, 2),
                    "cost_per_km": round(route_cost / distance, 4),
                }
            )
            for product in products:
                price_factor = product_price[product["product_id"]] * 0.01
                shipping_costs.append(
                    {
                        "warehouse_id": wh_id,
                        "customer_id": cust_id,
                        "product_id": product["product_id"],
                        "shipping_cost": round(route_cost + price_factor, 2),
                        "distance_km": round(distance, 2),
                        "delivery_time_days": delivery_days,
                    }
                )

    road_nodes = [
        {
            "node_id": warehouse["warehouse_id"],
            "name": warehouse["warehouse_name"],
            "latitude": round(warehouse_coords[warehouse["warehouse_id"]][0], 6),
            "longitude": round(warehouse_coords[warehouse["warehouse_id"]][1], 6),
        }
        for warehouse in warehouses
    ] + [
        {
            "node_id": customer["customer_id"],
            "name": customer["customer_name"],
            "latitude": round(customer_coords[customer["customer_id"]][0], 6),
            "longitude": round(customer_coords[customer["customer_id"]][1], 6),
        }
        for customer in customers
    ]

    for path in RAW_DIR.glob("*_metadata.json"):
        path.unlink()

    _write_csv("products.csv", ["product_id", "product_name", "category", "unit_price"], products)
    _write_csv(
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
    _write_csv("warehouses.csv", ["warehouse_id", "warehouse_name", "region", "storage_capacity"], warehouses)
    _write_csv("customers.csv", ["customer_id", "customer_name", "region"], customers)
    _write_csv("inventory.csv", ["warehouse_id", "product_id", "on_hand", "reserved"], inventory)
    _write_csv("demand_history.csv", ["product_id", "region", "period", "demand"], demand_history)
    _write_csv(
        "shipping_costs.csv",
        ["warehouse_id", "customer_id", "product_id", "shipping_cost", "distance_km", "delivery_time_days"],
        shipping_costs,
    )
    _write_csv("road_nodes.csv", ["node_id", "name", "latitude", "longitude"], road_nodes)
    _write_csv("road_edges.csv", ["from_node", "to_node", "distance_km", "cost_per_km"], road_edges)

    metadata = {
        "source": "Kaggle DataCo SMART Supply Chain",
        "kaggle_dataset": DATASET_SLUG,
        "notes": [
            "Derived from real transaction rows in DataCoSupplyChainDataset.csv.",
            f"Importer keeps top {TOP_PRODUCTS} products and top {TOP_CUSTOMERS} customers for app performance.",
            "Warehouses, inventory, shipping lanes, and route edges are derived from market, customer, order, and coordinate fields.",
        ],
        "source_rows": int(len(df)),
        "filtered_rows": int(len(working)),
        "latest_demand_period": latest_period,
        "row_counts": {
            "products": len(products),
            "suppliers": len(suppliers),
            "warehouses": len(warehouses),
            "customers": len(customers),
            "inventory": len(inventory),
            "demand_history": len(demand_history),
            "shipping_costs": len(shipping_costs),
            "road_nodes": len(road_nodes),
            "road_edges": len(road_edges),
        },
    }
    (RAW_DIR / "dataco_smart_supply_chain_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
