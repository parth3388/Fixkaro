from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.core.security import normalize_phone
from app.models.booking import BookingStatus
from app.schemas.service import ServiceOut


class BookingCreate(BaseModel):
    """Matches the #enquiry-form fields on index.html and contact.html."""

    full_name: str
    phone: str
    email: EmailStr | None = None
    city: str
    service: str
    message: str
    # Not collected by the current UI; accepted for forward compatibility.
    booking_date: date | None = None
    booking_time: time | None = None

    @field_validator("full_name")
    @classmethod
    def full_name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Enter the customer's full name.")
        return value[:120]

    @field_validator("phone")
    @classmethod
    def phone_is_valid(cls, value: str) -> str:
        return normalize_phone(value)

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("City is required.")
        return value[:80]

    @field_validator("service")
    @classmethod
    def service_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Select a service category.")
        return value

    @field_validator("message")
    @classmethod
    def message_long_enough(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Describe the issue in a few more words.")
        return value[:2000]


class BookingCancelRequest(BaseModel):
    """The phone number is required to prove the caller owns this booking."""

    phone: str

    @field_validator("phone")
    @classmethod
    def phone_is_valid(cls, value: str) -> str:
        return normalize_phone(value)


class BookingPublic(BaseModel):
    """Customer-facing booking view. Deliberately excludes phone, email and
    any internal database identifiers.
    """

    model_config = ConfigDict(from_attributes=True)

    booking_reference: str
    status: BookingStatus
    service: ServiceOut
    customer_name: str
    city: str
    notes: str
    booking_date: date | None
    booking_time: time | None
    created_at: datetime


class BookingCreateResponse(BaseModel):
    success: bool = True
    message: str = "Booking created successfully"
    booking: BookingPublic


class BookingGetResponse(BaseModel):
    success: bool = True
    booking: BookingPublic


class BookingCancelResponse(BaseModel):
    success: bool = True
    message: str = "Booking cancelled successfully"
    booking: BookingPublic
