from fastapi import APIRouter

router = APIRouter()

@router.get("/tests", tags=["pyats"])
async def get_tests():
    return [{"tests": {"test_1": "test_1_id", "test_2": "test_2_id"}}]