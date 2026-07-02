from fastapi import APIRouter

from app.schemas import DemandForecastRequest, ForecastRow
from app.services.data_service import load_dataset
from app.services.forecasting_service import forecast_demand


router = APIRouter(prefix="/forecast", tags=["Forecasting"])


@router.post("/demand", response_model=list[ForecastRow])
def demand_forecast(request: DemandForecastRequest) -> list[dict]:
    dataset = load_dataset()
    return forecast_demand(dataset["demand_history"], request.horizon_months, request.method)
