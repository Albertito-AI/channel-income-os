from __future__ import annotations

import math
from dataclasses import asdict
from typing import Any

from .models import ChannelSummary, VideoRecord
from .utils import percentile, safe_ratio


def _lane_summary(videos: list[VideoRecord], lane: str) -> dict[str, float]:
    cohort = [v for v in videos if v.lane == lane]
    views = sum(v.views for v in cohort)
    revenue = sum(v.estimated_revenue for v in cohort)
    retention = (
        sum(v.retention_ratio * v.views for v in cohort if v.duration_seconds > 0) /
        sum(v.views for v in cohort if v.duration_seconds > 0)
        if sum(v.views for v in cohort if v.duration_seconds > 0) else 0.0
    )
    return {
        "videos": len(cohort),
        "views": views,
        "revenue": revenue,
        "retention_ratio": retention,
        "effective_rpm": (revenue / views * 1000.0) if views else 0.0,
    }


def classify_video(
    video: VideoRecord,
    view_p75: float,
    view_p25: float,
    retention_p75: float,
    retention_p25: float,
    rpm_p95: float,
    minimum_sample: int,
) -> tuple[str, str, float]:
    if video.rights_status in {"hold", "uncleared", "disputed", "blocked"}:
        return (
            "RIGHTS_HOLD",
            "Do not scale, sponsor, license or deliberately promote this video until its rights record is cleared.",
            100.0,
        )
    if video.views < minimum_sample and video.effective_rpm >= rpm_p95 and video.estimated_revenue > 0:
        return (
            "REVENUE_AUDIT",
            "Audit the date-level revenue attribution and exclude this observation from forecasts until explained.",
            96.0,
        )
    if video.views >= view_p75 and video.retention_ratio and video.retention_ratio <= retention_p25:
        return (
            "REPAIR_RETENTION",
            "Inspect the first retention drop, improve the opening and route viewers to one tightly matched next video.",
            88.0,
        )
    if video.views <= view_p25 and video.retention_ratio >= retention_p75:
        return (
            "IMPROVE_DISCOVERY",
            "Test a clearer title and thumbnail while keeping the video substance fixed for a matched review window.",
            82.0,
        )
    if video.views >= view_p75 and video.retention_ratio >= retention_p75:
        return (
            "SCALE_WINNER",
            "Protect the winning promise, add a matched series route and create the next genuinely distinct follow-up.",
            78.0,
        )
    if video.ctr_percent and video.ctr_percent < 2.0 and video.impressions >= 1000:
        return (
            "PACKAGING_TEST",
            "Run a title or thumbnail test, changing one principal variable and recording the pre-change baseline.",
            70.0,
        )
    return (
        "MONITOR",
        "Keep in the weekly portfolio review; do not make changes without a specific hypothesis.",
        35.0,
    )


def analyze(
    videos: list[VideoRecord],
    summary: ChannelSummary,
    target_monthly_income: float,
    minimum_sample: int = 25,
) -> dict[str, Any]:
    view_values = [v.views for v in videos]
    retention_values = [v.retention_ratio for v in videos if v.duration_seconds > 0 and v.views > 0]
    rpm_values = [v.effective_rpm for v in videos if v.views > 0 and v.estimated_revenue > 0]
    view_p25 = percentile(view_values, 0.25)
    view_p75 = percentile(view_values, 0.75)
    retention_p25 = percentile(retention_values, 0.25)
    retention_p75 = percentile(retention_values, 0.75)
    rpm_p95 = percentile(rpm_values, 0.95)

    queue: list[dict[str, Any]] = []
    for video in videos:
        code, decision, priority = classify_video(
            video,
            view_p75,
            view_p25,
            retention_p75,
            retention_p25,
            rpm_p95,
            minimum_sample,
        )
        queue.append({
            "priority": priority,
            "code": code,
            "video_id": video.video_id,
            "title": video.title,
            "lane": video.lane,
            "views": video.views,
            "impressions": video.impressions,
            "ctr_percent": video.ctr_percent,
            "average_view_duration_seconds": video.average_view_duration_seconds,
            "retention_ratio": video.retention_ratio,
            "estimated_revenue": video.estimated_revenue,
            "effective_rpm": video.effective_rpm,
            "rights_status": video.rights_status,
            "decision": decision,
        })
    queue.sort(key=lambda item: (-item["priority"], -item["views"], item["title"].lower()))

    ranked_by_views = sorted(videos, key=lambda v: v.views, reverse=True)
    top10 = ranked_by_views[:10]
    captured_views = sum(v.views for v in videos)
    captured_revenue = sum(v.estimated_revenue for v in videos)
    top10_views = sum(v.views for v in top10)
    top10_revenue = sum(v.estimated_revenue for v in top10)

    effective_rpm = summary.effective_rpm
    views_required = (target_monthly_income / effective_rpm * 1000.0) if effective_rpm > 0 else None
    scenarios = []
    for rpm in [0.5, 1.0, 3.0, 5.0, 10.0]:
        scenarios.append({
            "rpm": rpm,
            "views_required": target_monthly_income / rpm * 1000.0,
        })

    report = {
        "target_monthly_income": target_monthly_income,
        "currency": summary.currency,
        "summary": asdict(summary),
        "effective_rpm": effective_rpm,
        "views_required_at_current_rpm": views_required,
        "target_multiple": safe_ratio(target_monthly_income, summary.estimated_revenue),
        "captured_video_count": len(videos),
        "captured_views": captured_views,
        "captured_revenue": captured_revenue,
        "captured_share_of_summary_views": safe_ratio(captured_views, summary.views),
        "captured_share_of_summary_revenue": safe_ratio(captured_revenue, summary.estimated_revenue),
        "top10_view_share": safe_ratio(top10_views, captured_views),
        "top10_revenue_share": safe_ratio(top10_revenue, captured_revenue),
        "learning": _lane_summary(videos, "learning"),
        "other": _lane_summary(videos, "other"),
        "thresholds": {
            "view_p25": view_p25,
            "view_p75": view_p75,
            "retention_p25": retention_p25,
            "retention_p75": retention_p75,
            "rpm_p95": rpm_p95,
            "minimum_sample_views": minimum_sample,
        },
        "rpm_scenarios": scenarios,
        "action_queue": queue,
    }
    return report
