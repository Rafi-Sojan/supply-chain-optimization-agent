from fastapi import APIRouter

from app.services.data_service import load_dataset
from app.services.inventory_service import build_reorder_plan


router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("")
def list_inventory() -> list[dict]:
    return load_dataset()["inventory"]


@router.get("/reorder-plan")
def reorder_plan() -> list[dict]:
    dataset = load_dataset()
    return build_reorder_plan(dataset["inventory"], dataset["demand_history"], dataset["suppliers"])
