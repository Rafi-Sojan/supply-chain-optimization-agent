from collections import defaultdict
from math import sqrt

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


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


def _linear_regression_forecast(values: list[int], horizon_months: int) -> int:
    if len(values) < 2:
        return values[-1] if values else 0

    model = LinearRegression()
    x = [[index] for index in range(len(values))]
    model.fit(x, values)
    forecast = model.predict([[len(values) - 1 + horizon_months]])[0]
    return max(0, round(float(forecast)))


def _rf_features(values: list[int], index: int) -> list[float]:
    lag_1 = values[index - 1] if index > 0 else values[0]
    window = values[max(0, index - 3):index] or [values[0]]
    rolling_3 = sum(window) / len(window)
    return [index, lag_1, rolling_3]


def _random_forest_forecast(values: list[int], horizon_months: int) -> int:
    if len(values) < 4:
        return _linear_regression_forecast(values, horizon_months)

    model = RandomForestRegressor(n_estimators=40, random_state=42, min_samples_leaf=1)
    x = [_rf_features(values, index) for index in range(1, len(values))]
    y = values[1:]
    model.fit(x, y)

    future_index = len(values) - 1 + horizon_months
    lag_1 = values[-1]
    rolling_3 = sum(values[-3:]) / min(3, len(values))
    forecast = model.predict([[future_index, lag_1, rolling_3]])[0]
    return max(0, round(float(forecast)))


def _xgboost_forecast(values: list[int], horizon_months: int) -> tuple[int, str]:
    if len(values) < 4:
        return _linear_regression_forecast(values, horizon_months), "fallback_linear_regression"

    try:
        from xgboost import XGBRegressor
    except ImportError:
        return _random_forest_forecast(values, horizon_months), "fallback_random_forest"

    model = XGBRegressor(
        n_estimators=40,
        max_depth=3,
        learning_rate=0.08,
        objective="reg:squarederror",
        random_state=42,
    )
    x = [_rf_features(values, index) for index in range(1, len(values))]
    y = values[1:]
    model.fit(x, y)

    future_index = len(values) - 1 + horizon_months
    lag_1 = values[-1]
    rolling_3 = sum(values[-3:]) / min(3, len(values))
    forecast = model.predict([[future_index, lag_1, rolling_3]])[0]
    return max(0, round(float(forecast))), "xgboost_regressor"


def _forecast_value(values: list[int], horizon_months: int, method: str) -> tuple[int, str]:
    if method == "moving_average":
        return _moving_average(values), "moving_average"
    if method == "linear_regression":
        return _linear_regression_forecast(values, horizon_months), "sklearn_linear_regression"
    if method == "random_forest":
        model_type = "sklearn_random_forest" if len(values) >= 4 else "fallback_linear_regression"
        return _random_forest_forecast(values, horizon_months), model_type
    if method == "xgboost":
        return _xgboost_forecast(values, horizon_months)
    return _linear_forecast(values, horizon_months), "linear_trend"


def _backtest_metrics(values: list[int], method: str) -> dict[str, float | None]:
    if len(values) < 4:
        return {"mae": None, "rmse": None, "mape": None}

    train = values[:-1]
    actual = values[-1]
    predicted, _ = _forecast_value(train, 1, method)
    mae = mean_absolute_error([actual], [predicted])
    rmse = sqrt(mean_squared_error([actual], [predicted]))
    mape = abs((actual - predicted) / actual) * 100 if actual else None
    return {
        "mae": round(float(mae), 2),
        "rmse": round(float(rmse), 2),
        "mape": round(float(mape), 2) if mape is not None else None,
    }


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
        forecast, model_type = _forecast_value(values, horizon_months, method)
        metrics = _backtest_metrics(values, method)
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
                "model_type": model_type,
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
                "mape": metrics["mape"],
            }
        )
    return forecasts
