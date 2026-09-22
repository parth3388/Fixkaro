from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Used by uptime monitors and load balancers to confirm the API is running.",
)
def health_check() -> HealthResponse:
    return HealthResponse(environment=settings.ENVIRONMENT)
