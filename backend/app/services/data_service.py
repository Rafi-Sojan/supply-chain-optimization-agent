import csv
import json
from pathlib import Path
from typing import Any


def _find_data_dir() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "data"
        if candidate.exists():
            return candidate
    return current.parents[3] / "data"


DATA_DIR = _find_data_dir()
RAW_DATA_DIR = DATA_DIR / "raw"

DATASET_FILES = {
    "products": ("products.csv", "sample_products.csv"),
    "suppliers": ("suppliers.csv", "sample_suppliers.csv"),
    "warehouses": ("warehouses.csv", "sample_warehouses.csv"),
    "customers": ("customers.csv", "sample_customers.csv"),
    "inventory": ("inventory.csv", "sample_inventory.csv"),
    "demand_history": ("demand_history.csv", "sample_demand_history.csv"),
    "shipping_costs": ("shipping_costs.csv", "sample_shipping_costs.csv"),
}

STRING_COLUMNS = {
    "product_id",
    "product_name",
    "category",
    "supplier_id",
    "supplier_name",
    "warehouse_id",
    "warehouse_name",
    "customer_id",
    "customer_name",
    "region",
    "period",
}

REQUIRED_COLUMNS = {
    "products": {"product_id", "product_name", "category", "unit_price"},
    "suppliers": {
        "supplier_id",
        "supplier_name",
        "product_id",
        "unit_cost",
        "lead_time_days",
        "reliability_score",
        "capacity",
        "quality_score",
        "past_delay_rate",
    },
    "warehouses": {"warehouse_id", "warehouse_name", "region", "storage_capacity"},
    "customers": {"customer_id", "customer_name", "region"},
    "inventory": {"warehouse_id", "product_id", "on_hand", "reserved"},
    "demand_history": {"product_id", "region", "period", "demand"},
    "shipping_costs": {
        "warehouse_id",
        "customer_id",
        "product_id",
        "shipping_cost",
        "distance_km",
        "delivery_time_days",
    },
}


def _coerce(key: str, value: str) -> Any:
    value = value.strip()
    if key in STRING_COLUMNS:
        return value
    if value == "":
        return value
    try:
        number = float(value)
    except ValueError:
        return value
    if number.is_integer():
        return int(number)
    return number


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: _coerce(key, value) for key, value in row.items()} for row in csv.DictReader(handle)]


def _real_dataset_available() -> bool:
    return any((RAW_DATA_DIR / filenames[0]).exists() for filenames in DATASET_FILES.values())


def _path_for(dataset_name: str, use_real_data: bool) -> Path:
    real_name, sample_name = DATASET_FILES[dataset_name]
    if use_real_data:
        return RAW_DATA_DIR / real_name
    return DATA_DIR / sample_name


def load_sample_dataset() -> dict[str, list[dict[str, Any]]]:
    return load_dataset(use_real_data=False)


def load_dataset(use_real_data: bool | None = None) -> dict[str, list[dict[str, Any]]]:
    real_data = _real_dataset_available() if use_real_data is None else use_real_data
    missing_files = [str(_path_for(name, real_data)) for name in DATASET_FILES if not _path_for(name, real_data).exists()]
    if missing_files:
        raise ValueError("Missing dataset files: " + ", ".join(missing_files))
    dataset = {name: read_csv(_path_for(name, real_data)) for name in DATASET_FILES}
    errors = validate_dataset(dataset)
    if errors:
        source = "real data/raw CSVs" if real_data else "sample CSVs"
        raise ValueError(f"Invalid {source}: " + "; ".join(errors))
    return dataset


def dataset_status() -> dict[str, Any]:
    real_data = _real_dataset_available()
    metadata = _active_metadata() if real_data else None
    files = {}
    for dataset_name, (real_name, sample_name) in DATASET_FILES.items():
        real_path = RAW_DATA_DIR / real_name
        sample_path = DATA_DIR / sample_name
        active_path = real_path if real_data else sample_path
        files[dataset_name] = {
            "expected_real_file": str(real_path),
            "sample_file": str(sample_path),
            "active_file": str(active_path),
            "exists": active_path.exists(),
        }

    try:
        dataset = load_dataset(use_real_data=real_data)
        errors = validate_dataset(dataset)
        row_counts = {name: len(rows) for name, rows in dataset.items()}
    except Exception as exc:
        errors = [str(exc)]
        row_counts = {}

    return {
        "source": "real" if real_data else "sample",
        "dataset_name": metadata.get("source") if metadata else "Sample CSVs",
        "dataset_metadata": metadata,
        "valid": not errors,
        "errors": errors,
        "row_counts": row_counts,
        "files": files,
        "required_columns": {name: sorted(columns) for name, columns in REQUIRED_COLUMNS.items()},
    }


def _active_metadata() -> dict[str, Any] | None:
    metadata_files = sorted(RAW_DATA_DIR.glob("*_metadata.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in metadata_files:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
    return None


def validate_dataset(dataset: dict[str, list[dict[str, Any]]]) -> list[str]:
    errors = []
    for name, required in REQUIRED_COLUMNS.items():
        rows = dataset.get(name, [])
        if not rows:
            errors.append(f"{name} has no rows")
            continue
        actual = set(rows[0])
        missing = required - actual
        if missing:
            errors.append(f"{name} missing columns: {', '.join(sorted(missing))}")

    if errors:
        return errors

    product_ids = {row["product_id"] for row in dataset["products"]}
    warehouse_ids = {row["warehouse_id"] for row in dataset["warehouses"]}
    customer_ids = {row["customer_id"] for row in dataset["customers"]}
    customer_regions = {row["region"] for row in dataset["customers"]}

    for table_name in ("suppliers", "inventory", "demand_history", "shipping_costs"):
        unknown_products = sorted({row["product_id"] for row in dataset[table_name]} - product_ids)
        if unknown_products:
            errors.append(f"{table_name} references unknown product_id values: {', '.join(unknown_products)}")

    unknown_inventory_warehouses = sorted({row["warehouse_id"] for row in dataset["inventory"]} - warehouse_ids)
    if unknown_inventory_warehouses:
        errors.append(f"inventory references unknown warehouse_id values: {', '.join(unknown_inventory_warehouses)}")

    unknown_shipping_warehouses = sorted({row["warehouse_id"] for row in dataset["shipping_costs"]} - warehouse_ids)
    if unknown_shipping_warehouses:
        errors.append(f"shipping_costs references unknown warehouse_id values: {', '.join(unknown_shipping_warehouses)}")

    unknown_shipping_customers = sorted({row["customer_id"] for row in dataset["shipping_costs"]} - customer_ids)
    if unknown_shipping_customers:
        errors.append(f"shipping_costs references unknown customer_id values: {', '.join(unknown_shipping_customers)}")

    unknown_demand_regions = sorted({row["region"] for row in dataset["demand_history"]} - customer_regions)
    if unknown_demand_regions:
        errors.append(f"demand_history references regions not present in customers: {', '.join(unknown_demand_regions)}")

    numeric_checks = {
        "products": ("unit_price",),
        "suppliers": ("unit_cost", "lead_time_days", "reliability_score", "capacity", "quality_score", "past_delay_rate"),
        "warehouses": ("storage_capacity",),
        "inventory": ("on_hand", "reserved"),
        "demand_history": ("demand",),
        "shipping_costs": ("shipping_cost", "distance_km", "delivery_time_days"),
    }
    for table_name, columns in numeric_checks.items():
        for index, row in enumerate(dataset[table_name], start=1):
            for column in columns:
                if not isinstance(row[column], int | float):
                    errors.append(f"{table_name} row {index} column {column} must be numeric")
                elif row[column] < 0:
                    errors.append(f"{table_name} row {index} column {column} cannot be negative")

    return errors
