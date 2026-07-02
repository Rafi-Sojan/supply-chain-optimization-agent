from collections import defaultdict


def _risk_level(trend_percentage: float) -> str:
    if trend_percentage >= 25:
        return "High"
    if trend_percentage >= 10:
        return "Medium"
    if trend_percentage <= -15:
        return "Low demand risk"
    return "Low"


def _linear_forecast(values: list[int], horizon_months: int) -> int:
    if len(values) < 2:
        return values[-1] if values else 0

    n = len(values)
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    numerator = sum((idx - x_mean) * (value - y_mean) for idx, value in enumerate(values))
    denominator = sum((idx - x_mean) ** 2 for idx in range(n)) or 1
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    forecast = intercept + slope * (n - 1 + horizon_months)
    return max(0, round(forecast))


def _moving_average(values: list[int], window: int = 3) -> int:
    if not values:
        return 0
    recent = values[-window:]
    return round(sum(recent) / len(recent))


def forecast_demand(
    demand_history: list[dict],
    horizon_months: int = 1,
    method: str = "linear_trend",
) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in demand_history:
        grouped[(row["product_id"], row["region"])].append(row)

    forecasts = []
    for (product_id, region), rows in sorted(grouped.items()):
        ordered = sorted(rows, key=lambda item: str(item["period"]))
        values = [int(item["demand"]) for item in ordered]
        previous = values[-1] if values else 0
        forecast = (
            _moving_average(values)
            if method == "moving_average"
            else _linear_forecast(values, horizon_months)
        )
        trend = round(((forecast - previous) / previous) * 100, 1) if previous else 0.0
        forecasts.append(
            {
                "product_id": product_id,
                "region": region,
                "previous_month_demand": previous,
                "forecasted_demand": forecast,
                "trend_percentage": trend,
                "risk_level": _risk_level(trend),
                "method": method,
            }
        )
    return forecasts
