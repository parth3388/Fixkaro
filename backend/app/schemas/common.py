from pydantic import BaseModel

from app.schemas.service import ServiceOut


class HealthResponse(BaseModel):
    success: bool = True
    status: str = "ok"
    environment: str


class ServiceListResponse(BaseModel):
    success: bool = True
    services: list[ServiceOut]


class ServiceDetailResponse(BaseModel):
    success: bool = True
    service: ServiceOut


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Shape returned for every 4xx/5xx response (see main.py exception handlers)."""

    success: bool = False
    error: ErrorDetail
