from fastapi import APIRouter

from app.services.data_service import dataset_status


router = APIRouter(prefix="/data", tags=["Data"])


@router.get("/status")
def status() -> dict:
    return dataset_status()
