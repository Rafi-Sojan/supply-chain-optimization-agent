from app.services.forecasting_service import forecast_demand
from app.services.inventory_service import build_reorder_plan
from app.services.optimization_service import optimize_warehouse_allocation
from app.services.supplier_ranking_service import rank_suppliers
from app.services.data_service import validate_dataset


def _dataset():
    return {
        "products": [{"product_id": "P1", "product_name": "Test Product", "category": "Test", "unit_price": 20}],
        "customers": [{"customer_id": "C1", "customer_name": "Test Customer", "region": "South"}],
        "warehouses": [{"warehouse_id": "W1", "warehouse_name": "Test Warehouse", "region": "South", "storage_capacity": 1000}],
        "inventory": [{"warehouse_id": "W1", "product_id": "P1", "on_hand": 100, "reserved": 0}],
        "suppliers": [
            {
                "supplier_id": "S1",
                "supplier_name": "Test Supplier",
                "product_id": "P1",
                "unit_cost": 10,
                "lead_time_days": 5,
                "reliability_score": 95,
                "capacity": 100,
                "quality_score": 92,
                "past_delay_rate": 3,
            }
        ],
        "demand_history": [
            {"product_id": "P1", "region": "South", "period": "2026-01-01", "demand": 30},
            {"product_id": "P1", "region": "South", "period": "2026-02-01", "demand": 40},
        ],
        "shipping_costs": [
            {
                "warehouse_id": "W1",
                "customer_id": "C1",
                "product_id": "P1",
                "shipping_cost": 2,
                "distance_km": 10,
                "delivery_time_days": 1,
            }
        ],
    }


def test_forecast_returns_growth_signal():
    result = forecast_demand(_dataset()["demand_history"])

    assert result[0]["forecasted_demand"] > 40
    assert result[0]["risk_level"] in {"Low", "Medium", "High"}


def test_inventory_reorder_plan_contains_business_metrics():
    dataset = _dataset()
    result = build_reorder_plan(dataset["inventory"], dataset["demand_history"], dataset["suppliers"])

    assert result[0]["reorder_point"] >= 0
    assert "stockout_risk" in result[0]


def test_supplier_ranking_scores_suppliers():
    result = rank_suppliers(_dataset()["suppliers"])

    assert result[0]["score"] > 0
    assert result[0]["risk_level"] == "Low"


def test_optimizer_allocates_low_cost_feasible_plan():
    result = optimize_warehouse_allocation(_dataset())

    assert result["status"] == "optimal"
    assert result["total_cost"] == 80
    assert result["allocations"][0]["quantity"] == 40


def test_dataset_validation_accepts_consistent_dataset():
    assert validate_dataset(_dataset()) == []


def test_dataset_validation_rejects_unknown_product_references():
    dataset = _dataset()
    dataset["inventory"][0]["product_id"] = "UNKNOWN"

    errors = validate_dataset(dataset)

    assert any("unknown product_id" in error for error in errors)
