from fastapi import APIRouter

from app.schemas import OptimizationRequest, OptimizationResponse
from app.services.data_service import load_dataset
from app.services.optimization_service import optimize_warehouse_allocation


router = APIRouter(prefix="/optimize", tags=["Optimization"])

RUN_HISTORY: list[dict] = []


@router.post("/warehouse-allocation", response_model=OptimizationResponse)
def warehouse_allocation(request: OptimizationRequest) -> dict:
    result = optimize_warehouse_allocation(
        load_dataset(),
        scenario_name=request.scenario_name,
        demand_multiplier=request.demand_multiplier,
        fuel_cost_multiplier=request.fuel_cost_multiplier,
        disabled_warehouses=request.disabled_warehouses,
    )
    RUN_HISTORY.append(
        {
            "run_id": len(RUN_HISTORY) + 1,
            "scenario_name": result["scenario_name"],
            "total_cost": result["total_cost"],
            "status": result["status"],
            "allocation_count": len(result["allocations"]),
            "unmet_demand_count": len(result["unmet_demand"]),
        }
    )
    return result


@router.get("/runs")
def optimization_runs() -> list[dict]:
    return RUN_HISTORY
