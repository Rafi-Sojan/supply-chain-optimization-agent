from collections import defaultdict
from copy import deepcopy


def _latest_demand_by_customer(demand_history: list[dict], customers: list[dict], multiplier: float) -> list[dict]:
    region_customer = {row["region"]: row["customer_id"] for row in customers}
    latest: dict[tuple[str, str], dict] = {}
    for row in demand_history:
        key = (row["product_id"], row["region"])
        if key not in latest or str(row["period"]) > str(latest[key]["period"]):
            latest[key] = row

    demand_rows = []
    for (product_id, region), row in latest.items():
        customer_id = region_customer.get(region)
        if customer_id:
            demand_rows.append(
                {
                    "customer_id": customer_id,
                    "product_id": product_id,
                    "demand": max(0, round(float(row["demand"]) * multiplier)),
                }
            )
    return demand_rows


def _recommendation(total_cost: float, unmet_demand: list[dict]) -> str:
    if unmet_demand:
        return "Increase inventory or add supplier capacity before accepting this plan."
    if total_cost > 0:
        return "Plan is feasible. Prioritize the lowest-cost warehouse lanes and monitor high-growth demand regions."
    return "No demand was allocated. Verify demand history and inventory inputs."


def _solve_with_ortools(
    available: dict[tuple[str, str], int],
    demand_remaining: dict[tuple[str, str], int],
    cost_rows: list[dict],
    scenario_name: str,
) -> dict | None:
    try:
        from ortools.linear_solver import pywraplp
    except ImportError:
        return None

    solver = pywraplp.Solver.CreateSolver("CBC_MIXED_INTEGER_PROGRAMMING")
    if solver is None:
        return None

    max_cost = max((float(row["shipping_cost"]) for row in cost_rows), default=1)
    unmet_penalty = max_cost * 100
    shipment_vars = {}
    unmet_vars = {}

    for row in cost_rows:
        supply_key = (row["warehouse_id"], row["product_id"])
        demand_key = (row["customer_id"], row["product_id"])
        if available.get(supply_key, 0) <= 0 or demand_remaining.get(demand_key, 0) <= 0:
            continue
        var_key = (row["warehouse_id"], row["customer_id"], row["product_id"])
        shipment_vars[var_key] = solver.IntVar(0, solver.infinity(), f"ship_{'_'.join(var_key)}")

    for demand_key, quantity in demand_remaining.items():
        unmet_vars[demand_key] = solver.IntVar(0, quantity, f"unmet_{'_'.join(demand_key)}")

    for supply_key, quantity in available.items():
        solver.Add(
            sum(var for key, var in shipment_vars.items() if (key[0], key[2]) == supply_key)
            <= quantity
        )

    for demand_key, quantity in demand_remaining.items():
        solver.Add(
            sum(var for key, var in shipment_vars.items() if (key[1], key[2]) == demand_key)
            + unmet_vars[demand_key]
            == quantity
        )

    cost_by_lane = {
        (row["warehouse_id"], row["customer_id"], row["product_id"]): float(row["shipping_cost"])
        for row in cost_rows
    }
    solver.Minimize(
        sum(cost_by_lane[key] * var for key, var in shipment_vars.items())
        + sum(unmet_penalty * var for var in unmet_vars.values())
    )

    status = solver.Solve()
    if status not in {pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE}:
        return None

    allocations = []
    for key, var in shipment_vars.items():
        quantity = round(var.solution_value())
        if quantity <= 0:
            continue
        unit_cost = round(cost_by_lane[key], 2)
        allocations.append(
            {
                "warehouse_id": key[0],
                "customer_id": key[1],
                "product_id": key[2],
                "quantity": quantity,
                "unit_shipping_cost": unit_cost,
                "total_cost": round(quantity * unit_cost, 2),
            }
        )

    unmet_demand = [
        {"customer_id": key[0], "product_id": key[1], "quantity": round(var.solution_value())}
        for key, var in unmet_vars.items()
        if round(var.solution_value()) > 0
    ]
    total_cost = round(sum(row["total_cost"] for row in allocations), 2)
    status_label = "infeasible" if unmet_demand else "optimal"

    return {
        "scenario_name": scenario_name,
        "total_cost": total_cost,
        "status": status_label,
        "allocations": allocations,
        "unmet_demand": unmet_demand,
        "recommendation": _recommendation(total_cost, unmet_demand),
    }


def optimize_warehouse_allocation(
    dataset: dict[str, list[dict]],
    scenario_name: str = "Base Case",
    demand_multiplier: float = 1.0,
    fuel_cost_multiplier: float = 1.0,
    disabled_warehouses: list[str] | None = None,
) -> dict:
    disabled = set(disabled_warehouses or [])
    inventory = [deepcopy(row) for row in dataset["inventory"] if row["warehouse_id"] not in disabled]
    demand_rows = _latest_demand_by_customer(dataset["demand_history"], dataset["customers"], demand_multiplier)
    costs = [
        {**row, "shipping_cost": float(row["shipping_cost"]) * fuel_cost_multiplier}
        for row in dataset["shipping_costs"]
        if row["warehouse_id"] not in disabled
    ]

    available: dict[tuple[str, str], int] = {
        (row["warehouse_id"], row["product_id"]): int(row["on_hand"]) - int(row.get("reserved", 0))
        for row in inventory
    }
    demand_remaining: dict[tuple[str, str], int] = {
        (row["customer_id"], row["product_id"]): int(row["demand"]) for row in demand_rows
    }

    cost_lookup = sorted(costs, key=lambda row: float(row["shipping_cost"]))
    ortools_result = _solve_with_ortools(dict(available), dict(demand_remaining), cost_lookup, scenario_name)
    if ortools_result is not None:
        return ortools_result

    allocations = []

    for cost_row in cost_lookup:
        wh_product = (cost_row["warehouse_id"], cost_row["product_id"])
        customer_product = (cost_row["customer_id"], cost_row["product_id"])
        supply = available.get(wh_product, 0)
        demand = demand_remaining.get(customer_product, 0)
        if supply <= 0 or demand <= 0:
            continue
        quantity = min(supply, demand)
        unit_cost = round(float(cost_row["shipping_cost"]), 2)
        allocations.append(
            {
                "warehouse_id": cost_row["warehouse_id"],
                "customer_id": cost_row["customer_id"],
                "product_id": cost_row["product_id"],
                "quantity": quantity,
                "unit_shipping_cost": unit_cost,
                "total_cost": round(quantity * unit_cost, 2),
            }
        )
        available[wh_product] -= quantity
        demand_remaining[customer_product] -= quantity

    unmet_demand = [
        {"customer_id": customer_id, "product_id": product_id, "quantity": quantity}
        for (customer_id, product_id), quantity in demand_remaining.items()
        if quantity > 0
    ]
    total_cost = round(sum(row["total_cost"] for row in allocations), 2)
    status = "infeasible" if unmet_demand else "optimal"

    return {
        "scenario_name": scenario_name,
        "total_cost": total_cost,
        "status": status,
        "allocations": allocations,
        "unmet_demand": unmet_demand,
        "recommendation": _recommendation(total_cost, unmet_demand),
    }


def summarize_allocations(allocations: list[dict]) -> dict[str, int]:
    summary: dict[str, int] = defaultdict(int)
    for row in allocations:
        key = f"{row['warehouse_id']}->{row['customer_id']}:{row['product_id']}"
        summary[key] += int(row["quantity"])
    return dict(summary)
