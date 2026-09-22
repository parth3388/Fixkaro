"""A single service booking created from the site's enquiry form."""

import enum
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy import Enum as SAEnum
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# Statuses a booking can still move out of. Anything not in this set is a
# terminal state (see booking_service.cancel_booking).
CANCELLABLE_STATUSES = {BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.ASSIGNED}


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_reference: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True, nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), index=True, nullable=False)

    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="booking_status", values_callable=lambda e: [m.value for m in e]),
        default=BookingStatus.PENDING,
        server_default=BookingStatus.PENDING.value,
        index=True,
        nullable=False,
    )

    # "City" is the only location field the current enquiry form collects.
    address_city: Mapped[str] = mapped_column(String(80), nullable=False)
    # The free-text "Tell us about the issue" / "Describe the issue" field.
    notes: Mapped[str] = mapped_column(Text, nullable=False)

    # Not collected by the current UI (no date/time picker exists yet).
    # Kept nullable so the team can fill them in after the confirmation
    # call described in the site's own "How it works" copy.
    booking_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    booking_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="bookings")
    service: Mapped["Service"] = relationship(back_populates="bookings")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Booking {self.booking_reference} {self.status}>"
