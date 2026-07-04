from typing import Any

from pydantic import BaseModel, Field


class DemandForecastRequest(BaseModel):
    horizon_months: int = Field(default=1, ge=1, le=12)
    method: str = Field(default="linear_trend", pattern="^(linear_trend|moving_average|linear_regression|random_forest|xgboost)$")


class ForecastRow(BaseModel):
    product_id: str
    region: str
    previous_month_demand: int
    forecasted_demand: int
    trend_percentage: float
    risk_level: str
    method: str
    model_type: str
    mae: float | None = None
    rmse: float | None = None
    mape: float | None = None


class OptimizationRequest(BaseModel):
    scenario_name: str = "Base Case"
    demand_multiplier: float = Field(default=1.0, gt=0)
    fuel_cost_multiplier: float = Field(default=1.0, gt=0)
    disabled_warehouses: list[str] = Field(default_factory=list)
    use_route_costs: bool = True
    route_algorithm: str = Field(default="dijkstra", pattern="^(dijkstra|astar)$")


class AllocationRow(BaseModel):
    warehouse_id: str
    customer_id: str
    product_id: str
    quantity: int
    unit_shipping_cost: float
    total_cost: float


class OptimizationResponse(BaseModel):
    scenario_name: str
    total_cost: float
    status: str
    allocations: list[AllocationRow]
    unmet_demand: list[dict[str, Any]]
    recommendation: str


class ScenarioRequest(OptimizationRequest):
    supplier_reliability_multiplier: float = Field(default=1.0, gt=0)


class ScenarioResponse(BaseModel):
    scenario_name: str
    base_cost: float
    scenario_cost: float
    cost_difference: float
    percentage_change: float
    changed_allocation_count: int
    risk_level: str
    recommendation: str
    base_result: OptimizationResponse
    scenario_result: OptimizationResponse
