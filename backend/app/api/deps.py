from fastapi import HTTPException, Query, status

from app.core.database import get_db  # re-exported for convenient single import point
from app.core.security import normalize_phone

__all__ = ["get_db", "phone_query_param"]


def phone_query_param(
    phone: str = Query(..., description="The mobile number used when the booking was created."),
) -> str:
    try:
        return normalize_phone(phone)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
