def _normalize(value: float, min_value: float, max_value: float, lower_is_better: bool = False) -> float:
    if max_value == min_value:
        return 1.0
    score = (value - min_value) / (max_value - min_value)
    return 1 - score if lower_is_better else score


def rank_suppliers(suppliers: list[dict]) -> list[dict]:
    if not suppliers:
        return []

    costs = [float(row["unit_cost"]) for row in suppliers]
    lead_times = [float(row["lead_time_days"]) for row in suppliers]
    capacities = [float(row["capacity"]) for row in suppliers]

    ranked = []
    for supplier in suppliers:
        cost_score = _normalize(float(supplier["unit_cost"]), min(costs), max(costs), lower_is_better=True)
        lead_time_score = _normalize(
            float(supplier["lead_time_days"]),
            min(lead_times),
            max(lead_times),
            lower_is_better=True,
        )
        capacity_score = _normalize(float(supplier["capacity"]), min(capacities), max(capacities))
        reliability_score = float(supplier["reliability_score"]) / 100
        quality_score = float(supplier["quality_score"]) / 100
        delay_penalty = float(supplier.get("past_delay_rate", 0)) / 100

        final_score = (
            0.30 * cost_score
            + 0.25 * reliability_score
            + 0.20 * lead_time_score
            + 0.15 * capacity_score
            + 0.10 * quality_score
            - 0.10 * delay_penalty
        )
        risk = "High" if reliability_score < 0.8 or delay_penalty > 0.15 else "Medium" if reliability_score < 0.9 else "Low"
        ranked.append(
            {
                **supplier,
                "score": round(final_score * 100, 2),
                "risk_level": risk,
                "selection_reason": (
                    "Strong cost, lead-time, reliability, capacity, and quality balance."
                    if risk == "Low"
                    else "Usable supplier, but monitor reliability and delay exposure."
                ),
            }
        )

    return sorted(ranked, key=lambda row: row["score"], reverse=True)
