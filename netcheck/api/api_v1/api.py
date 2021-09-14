from fastapi import APIRouter
from api.api_v1.endpoints import batfish, pyats
## File to include all routers

api_router = APIRouter()

# Add batfish endpoints
api_router.include_router(
    batfish.router,
    prefix="/batfish",
    tags=["batfish"],
    responses={404: {"description": "Not found"}},
)

# Add pyats endpoints
api_router.include_router(
    pyats.router,
    prefix="/pyats",
    tags=["pyats"],
    responses={404: {"description": "Not found"}},
)