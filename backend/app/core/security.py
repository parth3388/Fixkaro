"""Security-sensitive helpers: unguessable booking references and phone
normalisation used to verify a caller owns the booking they are looking up.

No password hashing or token auth is implemented here because the current
booking flow is anonymous (see BACKEND_ASSUMPTIONS.md). If admin
authentication is added later, it belongs in this module.
"""

import re
import secrets
import string

BOOKING_REFERENCE_PREFIX = "FIX-"
BOOKING_REFERENCE_LENGTH = 8
_REFERENCE_ALPHABET = string.ascii_uppercase + string.digits


def generate_booking_reference() -> str:
    """Generate a random, non-sequential booking reference such as FIX-7K2QANH4.

    Uses `secrets` (cryptographically strong) rather than `random` so booking
    references cannot be predicted or enumerated by an outside party.
    """
    suffix = "".join(secrets.choice(_REFERENCE_ALPHABET) for _ in range(BOOKING_REFERENCE_LENGTH))
    return f"{BOOKING_REFERENCE_PREFIX}{suffix}"


_PHONE_DIGITS_RE = re.compile(r"\D+")


def normalize_phone(raw_phone: str) -> str:
    """Reduce a phone number to its last 10 digits for storage/comparison.

    Accepts common Indian mobile input formats: "+91 88242 76600",
    "088242-76600", "8824276600", etc. Raises ValueError if fewer than 10
    digits remain, since that cannot be a valid mobile number. Callers in the
    API layer are responsible for translating that into an HTTP error.
    """
    digits = _PHONE_DIGITS_RE.sub("", raw_phone or "")
    if len(digits) < 10:
        raise ValueError("Enter a valid 10-digit mobile number.")
    return digits[-10:]
