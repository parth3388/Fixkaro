from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, phone_query_param
from app.schemas.booking import (
    BookingCancelRequest,
    BookingCancelResponse,
    BookingCreate,
    BookingCreateResponse,
    BookingGetResponse,
)
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])

_NOT_FOUND_DETAIL = "No booking found for that reference and mobile number."


@router.post(
    "",
    response_model=BookingCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a booking",
    description="Submits the enquiry/booking form. Validates the service, "
    "creates or reuses the customer record, and returns a unique booking reference.",
    responses={400: {"description": "Unknown service category"}},
)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)) -> BookingCreateResponse:
    try:
        booking = booking_service.create_booking(db, payload)
    except booking_service.ServiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{exc}' is not a recognised service category.",
        ) from exc
    return BookingCreateResponse(booking=booking_service.booking_to_public(booking))


@router.get(
    "/{booking_reference}",
    response_model=BookingGetResponse,
    summary="Track a booking",
    description="Used by track.html. Requires the mobile number the booking was made with, "
    "so a booking reference alone cannot be used to look up someone else's booking.",
    responses={404: {"description": "No matching booking"}},
)
def get_booking(
    booking_reference: str,
    phone: str = Depends(phone_query_param),
    db: Session = Depends(get_db),
) -> BookingGetResponse:
    booking = booking_service.get_booking_for_owner(db, booking_reference=booking_reference, phone=phone)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND_DETAIL)
    return BookingGetResponse(booking=booking_service.booking_to_public(booking))


@router.post(
    "/{booking_reference}/cancel",
    response_model=BookingCancelResponse,
    summary="Cancel a booking",
    description="Requires the mobile number the booking was made with. "
    "Only PENDING, CONFIRMED or ASSIGNED bookings can be cancelled.",
    responses={404: {"description": "No matching booking"}, 409: {"description": "Booking is not cancellable"}},
)
def cancel_booking(
    booking_reference: str, payload: BookingCancelRequest, db: Session = Depends(get_db)
) -> BookingCancelResponse:
    try:
        booking = booking_service.cancel_booking(db, booking_reference=booking_reference, phone=payload.phone)
    except booking_service.BookingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=_NOT_FOUND_DETAIL) from exc
    except booking_service.BookingNotCancellableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return BookingCancelResponse(booking=booking_service.booking_to_public(booking))
