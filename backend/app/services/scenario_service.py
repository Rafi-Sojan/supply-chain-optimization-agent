from copy import deepcopy

from app.services.optimization_service import optimize_warehouse_allocation, summarize_allocations


def run_scenario(dataset: dict, request: dict) -> dict:
    base_result = optimize_warehouse_allocation(dataset, scenario_name="Base Case")

    scenario_dataset = deepcopy(dataset)
    reliability_multiplier = float(request.get("supplier_reliability_multiplier", 1.0))
    for supplier in scenario_dataset["suppliers"]:
        supplier["reliability_score"] = min(100, round(float(supplier["reliability_score"]) * reliability_multiplier, 1))

    scenario_result = optimize_warehouse_allocation(
        scenario_dataset,
        scenario_name=request.get("scenario_name", "Scenario"),
        demand_multiplier=float(request.get("demand_multiplier", 1.0)),
        fuel_cost_multiplier=float(request.get("fuel_cost_multiplier", 1.0)),
        disabled_warehouses=list(request.get("disabled_warehouses", [])),
    )

    base_cost = float(base_result["total_cost"])
    scenario_cost = float(scenario_result["total_cost"])
    difference = round(scenario_cost - base_cost, 2)
    percentage_change = round((difference / base_cost) * 100, 2) if base_cost else 0.0

    base_allocations = summarize_allocations(base_result["allocations"])
    scenario_allocations = summarize_allocations(scenario_result["allocations"])
    changed = sum(
        1 for key in set(base_allocations) | set(scenario_allocations)
        if base_allocations.get(key, 0) != scenario_allocations.get(key, 0)
    )

    risk_level = "High" if scenario_result["unmet_demand"] or percentage_change > 20 else "Medium" if percentage_change > 8 else "Low"
    recommendation = (
        "Scenario is risky. Add inventory, restore warehouse capacity, or renegotiate high-cost lanes."
        if risk_level == "High"
        else "Scenario is manageable. Review allocation changes and protect the best-performing lanes."
    )

    return {
        "scenario_name": scenario_result["scenario_name"],
        "base_cost": base_cost,
        "scenario_cost": scenario_cost,
        "cost_difference": difference,
        "percentage_change": percentage_change,
        "changed_allocation_count": changed,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "base_result": base_result,
        "scenario_result": scenario_result,
    }
