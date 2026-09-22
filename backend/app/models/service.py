"""The fixed catalog of service categories offered on the site.

This mirrors the <select id="category"> options already present in
index.html and contact.html (see BACKEND_ASSUMPTIONS.md). There is no
per-service pricing here: pricing on plans.html is a separate, static
subscription-plan table rendered entirely client-side and is out of scope
for this backend (no booking/payment action is attached to it).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="service")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Service {self.slug}>"
