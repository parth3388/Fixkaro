from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import ServiceDetailResponse, ServiceListResponse
from app.schemas.service import ServiceOut
from app.services import service_service

router = APIRouter(prefix="/services", tags=["services"])


@router.get(
    "",
    response_model=ServiceListResponse,
    summary="List bookable services",
    description="Returns the active service categories shown in the site's booking form.",
)
def list_services(db: Session = Depends(get_db)) -> ServiceListResponse:
    services = service_service.list_active_services(db)
    return ServiceListResponse(services=[ServiceOut.model_validate(s) for s in services])


@router.get(
    "/{slug}",
    response_model=ServiceDetailResponse,
    summary="Get a single service by slug",
    responses={404: {"description": "Service not found"}},
)
def get_service(slug: str, db: Session = Depends(get_db)) -> ServiceDetailResponse:
    service = service_service.get_service_by_slug(db, slug)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")
    return ServiceDetailResponse(service=ServiceOut.model_validate(service))
