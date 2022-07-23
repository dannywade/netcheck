from fastapi import APIRouter

router = APIRouter()


@router.get("/interfaces", tags=["analysis"])
async def read_interfaces():
    return [{"interfaces": "fake_interface_Gig1/0/1"}]
