from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import data, forecast, inventory, optimize, products, routes, scenarios, suppliers
from app.services.data_service import load_dataset
from app.services.forecasting_service import forecast_demand
from app.services.inventory_service import build_reorder_plan
from app.services.optimization_service import optimize_warehouse_allocation
from app.services.supplier_ranking_service import rank_suppliers


app = FastAPI(
    title="Supply Chain Optimization Platform",
    description="Forecasting, inventory planning, supplier ranking, warehouse optimization, and scenario simulation APIs.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(forecast.router)
app.include_router(optimize.router)
app.include_router(scenarios.router)
app.include_router(data.router)
app.include_router(routes.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "Supply Chain Optimization Platform API",
        "status": "running",
        "docs": "/docs",
        "dashboard_summary": "/dashboard/summary",
    }


@app.get("/dashboard/summary")
def dashboard_summary() -> dict:
    dataset = load_dataset()
    base_optimization = optimize_warehouse_allocation(dataset)
    forecasts = forecast_demand(dataset["demand_history"])
    reorder_plan = build_reorder_plan(dataset["inventory"], dataset["demand_history"], dataset["suppliers"])
    ranked_suppliers = rank_suppliers(dataset["suppliers"])

    high_risk_inventory = sum(1 for row in reorder_plan if row["stockout_risk"] == "High")
    high_growth_forecasts = sum(1 for row in forecasts if row["trend_percentage"] >= 10)

    return {
        "total_products": len(dataset["products"]),
        "total_suppliers": len(dataset["suppliers"]),
        "total_warehouses": len(dataset["warehouses"]),
        "optimized_cost": base_optimization["total_cost"],
        "optimization_status": base_optimization["status"],
        "high_risk_inventory_items": high_risk_inventory,
        "high_growth_forecasts": high_growth_forecasts,
        "best_supplier": ranked_suppliers[0] if ranked_suppliers else None,
        "recommendation": base_optimization["recommendation"],
    }
