"""Booking lifecycle: creation, owner-verified lookup, and cancellation.

Raises small domain-specific exceptions instead of FastAPI's HTTPException so
this module stays framework-agnostic; the API layer (app/api/routes/bookings.py)
translates them into HTTP responses.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import generate_booking_reference
from app.models.booking import CANCELLABLE_STATUSES, Booking, BookingStatus
from app.models.customer import Customer
from app.schemas.booking import BookingCreate, BookingPublic
from app.schemas.service import ServiceOut
from app.services.service_service import find_service_by_name_or_slug


class ServiceNotFoundError(Exception):
    """Raised when the submitted `service` does not match any active service."""


class BookingNotFoundError(Exception):
    """Raised when no booking matches the given reference + phone combination."""


class BookingNotCancellableError(Exception):
    """Raised when a booking is already in a terminal state."""

    def __init__(self, status: BookingStatus):
        self.status = status
        super().__init__(f"Booking is already {status.value} and cannot be cancelled.")


_MAX_REFERENCE_ATTEMPTS = 5


def _unique_booking_reference(db: Session) -> str:
    for _ in range(_MAX_REFERENCE_ATTEMPTS):
        candidate = generate_booking_reference()
        exists = db.execute(
            select(Booking.id).where(Booking.booking_reference == candidate)
        ).scalar_one_or_none()
        if exists is None:
            return candidate
    # Astronomically unlikely with a 36^8 keyspace, but fail loudly rather
    # than silently reuse a reference if it ever happens.
    raise RuntimeError("Could not generate a unique booking reference.")


def _get_or_create_customer(db: Session, *, full_name: str, phone: str, email: str | None) -> Customer:
    customer = db.execute(select(Customer).where(Customer.phone == phone)).scalar_one_or_none()
    if customer is None:
        customer = Customer(full_name=full_name, phone=phone, email=email)
        db.add(customer)
        db.flush()
        return customer

    # Keep the customer record current for repeat bookers.
    customer.full_name = full_name
    if email:
        customer.email = email
    db.flush()
    return customer


def booking_to_public(booking: Booking) -> BookingPublic:
    return BookingPublic(
        booking_reference=booking.booking_reference,
        status=booking.status,
        service=ServiceOut.model_validate(booking.service),
        customer_name=booking.customer.full_name,
        city=booking.address_city,
        notes=booking.notes,
        booking_date=booking.booking_date,
        booking_time=booking.booking_time,
        created_at=booking.created_at,
    )


def create_booking(db: Session, payload: BookingCreate) -> Booking:
    service = find_service_by_name_or_slug(db, payload.service)
    if service is None:
        raise ServiceNotFoundError(payload.service)

    customer = _get_or_create_customer(
        db, full_name=payload.full_name, phone=payload.phone, email=payload.email
    )

    booking = Booking(
        booking_reference=_unique_booking_reference(db),
        customer_id=customer.id,
        service_id=service.id,
        status=BookingStatus.PENDING,
        address_city=payload.city,
        notes=payload.message,
        booking_date=payload.booking_date,
        booking_time=payload.booking_time,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def get_booking_for_owner(db: Session, *, booking_reference: str, phone: str) -> Booking | None:
    """Return the booking only if `phone` matches the booking's customer.

    Returning None (rather than distinguishing "not found" from "wrong
    phone") deliberately avoids letting a caller use this endpoint to probe
    whether a given reference exists.
    """
    stmt = (
        select(Booking)
        .join(Customer, Booking.customer_id == Customer.id)
        .where(Booking.booking_reference == booking_reference.strip().upper(), Customer.phone == phone)
    )
    return db.execute(stmt).scalar_one_or_none()


def cancel_booking(db: Session, *, booking_reference: str, phone: str) -> Booking:
    booking = get_booking_for_owner(db, booking_reference=booking_reference, phone=phone)
    if booking is None:
        raise BookingNotFoundError(booking_reference)

    if booking.status not in CANCELLABLE_STATUSES:
        raise BookingNotCancellableError(booking.status)

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.now(UTC)
    db.commit()
    db.refresh(booking)
    return booking
