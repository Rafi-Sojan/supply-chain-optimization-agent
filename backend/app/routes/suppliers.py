from fastapi import APIRouter

from app.services.data_service import load_dataset
from app.services.supplier_ranking_service import rank_suppliers


router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("")
def list_suppliers() -> list[dict]:
    return load_dataset()["suppliers"]


@router.get("/ranking")
def supplier_ranking() -> list[dict]:
    return rank_suppliers(load_dataset()["suppliers"])
