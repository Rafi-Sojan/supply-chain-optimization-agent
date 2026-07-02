from fastapi import APIRouter

from app.services.data_service import load_dataset


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
def list_products() -> list[dict]:
    return load_dataset()["products"]
