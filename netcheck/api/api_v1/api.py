from fastapi import APIRouter
from api.api_v1.endpoints import analysis, validation, inventory

## File to include all routers

api_router = APIRouter()

# Add analysis endpoints
api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)

# Add validation endpoints
api_router.include_router(
    validation.router,
    prefix="/validation",
    tags=["validation"],
    responses={404: {"description": "Not found"}},
)

# Add inventory endpoints
api_router.include_router(
    inventory.router,
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
)
