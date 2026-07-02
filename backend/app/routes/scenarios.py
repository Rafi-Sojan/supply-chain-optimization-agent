from fastapi import APIRouter

from app.schemas import ScenarioRequest, ScenarioResponse
from app.services.data_service import load_dataset
from app.services.scenario_service import run_scenario


router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.post("/run", response_model=ScenarioResponse)
def scenario_run(request: ScenarioRequest) -> dict:
    return run_scenario(load_dataset(), request.model_dump())
