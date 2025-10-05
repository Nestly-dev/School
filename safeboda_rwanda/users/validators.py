import re

RW_PHONE_RE_E164 = re.compile(r"^\+2507\d{8}$")   # +2507XXXXXXXX (13 chars)
RW_PHONE_RE_LOCAL_10 = re.compile(r"^07\d{8}$")   # 07XXXXXXXX
RW_PHONE_RE_LOCAL_9 = re.compile(r"^7\d{8}$")     # 7XXXXXXXX
RW_PHONE_RE_250 = re.compile(r"^2507\d{8}$")      # 2507XXXXXXXX


def is_valid_rwanda_phone(value: str) -> bool:
    if not value:
        return False
    value = value.strip()
    return any(
        regex.match(value)
        for regex in (RW_PHONE_RE_E164, RW_PHONE_RE_LOCAL_10, RW_PHONE_RE_LOCAL_9, RW_PHONE_RE_250)
    )


def normalize_phone_e164_rw(value: str) -> str:
    """
    Normalize to E.164 +2507XXXXXXXX.
    Accepts: +2507XXXXXXXX, 2507XXXXXXXX, 07XXXXXXXX, 7XXXXXXXX.
    """
    if not value:
        raise ValueError("Phone value required.")
    v = value.strip()
    if RW_PHONE_RE_E164.match(v):
        return v
    if RW_PHONE_RE_250.match(v):
        return f"+{v}"
    if RW_PHONE_RE_LOCAL_10.match(v):
        return f"+250{v[1:]}"
    if RW_PHONE_RE_LOCAL_9.match(v):
        return f"+250{v}"
    raise ValueError("Unsupported phone format.")


def is_valid_national_id(value: str) -> bool:
    """Basic RW NID check: 16 digits."""
    if not value:
        return False
    v = value.strip()
    return v.isdigit() and len(v) == 16
