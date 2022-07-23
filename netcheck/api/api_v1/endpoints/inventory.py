from fastapi import APIRouter, HTTPException, Response
from sqlmodel import Session, select
from backend.models import DeviceInventory
from backend.db import engine
from fastapi_pagination import Page, add_pagination, paginate
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.get("/devices", response_model=Page[DeviceInventory], tags=["inventory"])
def get_inventory_results():
    with Session(engine) as session:
        results = session.exec(select(DeviceInventory)).all()
        return paginate(results)


@router.get("/devices/{device_id}", response_model=DeviceInventory, tags=["inventory"])
def get_single_test_result(device_id: int):
    with Session(engine) as session:
        test_result = session.get(DeviceInventory, device_id)
        if not test_result:
            raise HTTPException(status_code=404, detail="No test results found")
        return test_result


@router.delete(
    "/devices/{device_id}",
    # response_model=DeviceInventory,
    tags=["inventory"],
)
def delete_single_test_result(device_id: int):
    with Session(engine) as session:
        statement = select(DeviceInventory).where(
            DeviceInventory.device_id == device_id
        )
        results = session.exec(statement)
        device_result = results.one()

        session.delete(device_result)
        session.commit()

        if device_result is None:
            raise HTTPException(status_code=404, detail="No test results found")

        return Response(status_code=HTTP_204_NO_CONTENT)


add_pagination(router)
