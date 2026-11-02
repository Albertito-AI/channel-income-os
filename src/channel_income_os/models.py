from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VideoRecord:
    video_id: str
    title: str
    publish_date: str = ""
    duration_seconds: float = 0.0
    views: int = 0
    watch_hours: float = 0.0
    average_view_duration_seconds: float = 0.0
    estimated_revenue: float = 0.0
    rpm: float = 0.0
    impressions: int = 0
    ctr_percent: float = 0.0
    monetised_playbacks: int = 0
    lane: str = "other"
    rights_status: str = "unknown"
    source_row: dict[str, Any] = field(default_factory=dict)

    @property
    def retention_ratio(self) -> float:
        if self.duration_seconds <= 0:
            return 0.0
        return max(0.0, min(1.5, self.average_view_duration_seconds / self.duration_seconds))

    @property
    def effective_rpm(self) -> float:
        if self.views <= 0:
            return 0.0
        return (self.estimated_revenue / self.views) * 1000.0


@dataclass(slots=True)
class ChannelSummary:
    period_start: str = ""
    period_end: str = ""
    subscribers: int = 0
    views: int = 0
    watch_hours: float = 0.0
    estimated_revenue: float = 0.0
    impressions: int = 0
    ctr_percent: float = 0.0
    average_view_duration_seconds: float = 0.0
    returning_viewers: int = 0
    new_viewers: int = 0
    currency: str = "USD"

    @property
    def effective_rpm(self) -> float:
        if self.views <= 0:
            return 0.0
        return (self.estimated_revenue / self.views) * 1000.0
