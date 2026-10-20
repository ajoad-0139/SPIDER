import re
from typing import Optional


def clean_text(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def parse_price(value):
    cleaned = re.sub(r"[^\d.]", "", str(value or ""))
    if not cleaned:
        raise ValueError(f"Cannot parse price from {value!r}")
    return float(cleaned)


def parse_availability(value):
    return clean_text(value).lower().startswith("in stock")