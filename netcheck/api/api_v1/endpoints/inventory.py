from fastapi import APIRouter
from sqlmodel import Session, select
from backend.models import DeviceInventory
from backend.db import engine
from fastapi_pagination import Page, add_pagination, paginate

router = APIRouter()


@router.get("/devices", response_model=Page[DeviceInventory], tags=["inventory"])
def get_inventory_results():
    with Session(engine) as session:
        results = session.exec(select(DeviceInventory)).all()
        return paginate(results)


add_pagination(router)
