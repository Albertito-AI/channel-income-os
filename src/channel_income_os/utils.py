from __future__ import annotations

import math
import re
from typing import Iterable


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def parse_number(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip()
    if not text or text in {"-", "—", "–", "N/A", "n/a"}:
        return default
    text = text.replace(",", "").replace("%", "")
    text = re.sub(r"^[^0-9+\-.]+", "", text)
    text = re.sub(r"[^0-9eE+\-.]+$", "", text)
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def parse_int(value: object, default: int = 0) -> int:
    return int(round(parse_number(value, float(default))))


def parse_duration(value: object) -> float:
    """Parse seconds, H:MM:SS, M:SS, or ISO 8601 PT#H#M#S."""
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    if re.fullmatch(r"\d+(\.\d+)?", text):
        return float(text)
    iso = re.fullmatch(
        r"PT(?:(?P<h>\d+(?:\.\d+)?)H)?(?:(?P<m>\d+(?:\.\d+)?)M)?(?:(?P<s>\d+(?:\.\d+)?)S)?",
        text,
        flags=re.IGNORECASE,
    )
    if iso:
        return (
            float(iso.group("h") or 0) * 3600
            + float(iso.group("m") or 0) * 60
            + float(iso.group("s") or 0)
        )
    if ":" in text:
        parts = text.split(":")
        try:
            numbers = [float(p) for p in parts]
        except ValueError:
            return 0.0
        if len(numbers) == 3:
            return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
        if len(numbers) == 2:
            return numbers[0] * 60 + numbers[1]
    return 0.0


def format_duration(seconds: float) -> str:
    seconds_i = max(0, int(round(seconds)))
    h, rem = divmod(seconds_i, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def percentile(values: Iterable[float], p: float) -> float:
    data = sorted(float(v) for v in values)
    if not data:
        return 0.0
    if len(data) == 1:
        return data[0]
    p = max(0.0, min(1.0, p))
    index = (len(data) - 1) * p
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return data[lower]
    weight = index - lower
    return data[lower] * (1 - weight) + data[upper] * weight


def safe_ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0
