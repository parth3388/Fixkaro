"""Customer identity captured from the enquiry/booking form.

There is no login/account system on the frontend (see BACKEND_ASSUMPTIONS.md),
so this table simply de-duplicates repeat bookers by phone number. It is
named `Customer` rather than `User` because it holds no credentials.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    # Normalised to the last 10 digits by app.core.security.normalize_phone.
    phone: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Customer {self.phone}>"
