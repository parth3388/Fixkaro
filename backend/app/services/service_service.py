"""Read-only lookups against the static service catalog."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service


def list_active_services(db: Session) -> list[Service]:
    stmt = select(Service).where(Service.is_active.is_(True)).order_by(Service.id)
    return list(db.execute(stmt).scalars().all())


def get_service_by_slug(db: Session, slug: str) -> Service | None:
    stmt = select(Service).where(Service.slug == slug, Service.is_active.is_(True))
    return db.execute(stmt).scalar_one_or_none()


def find_service_by_name_or_slug(db: Session, value: str) -> Service | None:
    """Match the raw text a <select> sends: either the option's visible label
    (e.g. "AC & Cooling") or a slug (e.g. "ac-cooling"), case-insensitively.
    """
    normalized = value.strip().lower()
    stmt = select(Service).where(Service.is_active.is_(True))
    for service in db.execute(stmt).scalars().all():
        if service.name.lower() == normalized or service.slug.lower() == normalized:
            return service
    return None
