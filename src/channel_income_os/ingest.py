from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable

from .models import ChannelSummary, VideoRecord
from .utils import norm, parse_duration, parse_int, parse_number


ALIASES = {
    "video_id": ["content", "videoid", "video id", "id"],
    "title": ["videotitle", "video title", "title"],
    "publish_date": ["videopublishtime", "video publish time", "publishdate", "publishedat"],
    "duration": ["duration", "videoduration", "length"],
    "revenue": ["estimatedrevenue", "estimated revenue", "revenue"],
    "rpm": ["rpm", "revenueper1000views"],
    "views": ["views"],
    "watch_hours": ["watchtimehours", "watch time hours", "watchtime"],
    "avg_duration": ["averageviewduration", "average view duration", "avgviewduration"],
    "impressions": ["impressions"],
    "ctr": ["impressionsclickthroughrate", "impressions click-through rate", "ctr"],
    "monetised_playbacks": [
        "estimatedmonetisedplaybacks",
        "estimated monetized playbacks",
        "estimated monetised playbacks",
        "monetizedplaybacks",
    ],
}

SUMMARY_ALIASES = {
    "period_start": ["periodstart", "startdate", "start"],
    "period_end": ["periodend", "enddate", "end"],
    "subscribers": ["subscribers", "subscribercount"],
    "views": ["views"],
    "watch_hours": ["watchhours", "watchtimehours", "watchtime"],
    "estimated_revenue": ["estimatedrevenue", "revenue"],
    "impressions": ["impressions"],
    "ctr_percent": ["ctr", "impressionsclickthroughrate"],
    "average_view_duration_seconds": ["averageviewduration", "avgviewduration"],
    "returning_viewers": ["returningviewers"],
    "new_viewers": ["newviewers"],
    "currency": ["currency"],
}


def _find_column(fieldnames: Iterable[str], aliases: Iterable[str]) -> str | None:
    normalized = {norm(name): name for name in fieldnames if name}
    for alias in aliases:
        key = norm(alias)
        if key in normalized:
            return normalized[key]
    # Currency-labelled columns often start with the metric.
    for key, original in normalized.items():
        for alias in aliases:
            if key.startswith(norm(alias)):
                return original
    return None


def _detect_header(rows: list[list[str]]) -> tuple[int, list[str]]:
    for index, row in enumerate(rows[:20]):
        normalized = {norm(cell) for cell in row}
        if "views" in normalized and (
            "content" in normalized
            or "videoid" in normalized
            or "videotitle" in normalized
            or "title" in normalized
        ):
            return index, row
    raise ValueError(
        "Could not find a YouTube video-table header. Export an Advanced Mode table "
        "that includes at least video ID/title and Views."
    )


def load_videos(path: Path, learning_terms: list[str] | None = None) -> list[VideoRecord]:
    learning_terms = [term.lower().strip() for term in (learning_terms or ["learning with", "explained", "case", "law", "legal"])]

    def matches_learning_term(title: str) -> bool:
        lowered = title.lower()
        for term in learning_terms:
            if not term:
                continue
            if " " in term:
                if term in lowered:
                    return True
            elif re.search(rf"\\b{re.escape(term)}\\b", lowered):
                return True
        return False
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.reader(handle))
    if not raw_rows:
        raise ValueError(f"{path} is empty.")
    header_index, header = _detect_header(raw_rows)
    rows = raw_rows[header_index + 1 :]
    columns = {key: _find_column(header, aliases) for key, aliases in ALIASES.items()}
    if not columns["views"] or not (columns["video_id"] or columns["title"]):
        raise ValueError("The video export needs Views and either Content/Video ID or Video title.")

    result: list[VideoRecord] = []
    for values in rows:
        if not any(str(v).strip() for v in values):
            continue
        padded = values + [""] * max(0, len(header) - len(values))
        row = dict(zip(header, padded))
        title = str(row.get(columns["title"] or "", "")).strip()
        video_id = str(row.get(columns["video_id"] or "", "")).strip()
        # Skip total rows and malformed footer lines.
        if title.lower() == "total" or video_id.lower() == "total":
            continue
        if title.lower().startswith("showing top ") or video_id.lower().startswith("showing top "):
            continue
        if not title and not video_id:
            continue
        lane = "learning" if matches_learning_term(title) else "other"
        record = VideoRecord(
            video_id=video_id or f"title:{title}",
            title=title or video_id,
            publish_date=str(row.get(columns["publish_date"] or "", "")).strip(),
            duration_seconds=parse_duration(row.get(columns["duration"] or "")),
            views=parse_int(row.get(columns["views"] or "")),
            watch_hours=parse_number(row.get(columns["watch_hours"] or "")),
            average_view_duration_seconds=parse_duration(row.get(columns["avg_duration"] or "")),
            estimated_revenue=parse_number(row.get(columns["revenue"] or "")),
            rpm=parse_number(row.get(columns["rpm"] or "")),
            impressions=parse_int(row.get(columns["impressions"] or "")),
            ctr_percent=parse_number(row.get(columns["ctr"] or "")),
            monetised_playbacks=parse_int(row.get(columns["monetised_playbacks"] or "")),
            lane=lane,
            source_row=row,
        )
        result.append(record)
    if not result:
        raise ValueError("No usable video rows were found.")
    return result


def load_summary(path: Path | None, videos: list[VideoRecord], currency: str) -> tuple[ChannelSummary, list[str]]:
    warnings: list[str] = []
    if path is None:
        warnings.append(
            "No channel summary export supplied. Aggregate values were reconstructed from the video table "
            "and may understate the channel if Studio capped the export."
        )
        views = sum(v.views for v in videos)
        revenue = sum(v.estimated_revenue for v in videos)
        watch_hours = sum(v.watch_hours for v in videos)
        impressions = sum(v.impressions for v in videos)
        avg_duration = (
            sum(v.average_view_duration_seconds * v.views for v in videos) / views if views else 0.0
        )
        ctr = (
            sum(v.ctr_percent * v.impressions for v in videos) / impressions if impressions else 0.0
        )
        return ChannelSummary(
            views=views,
            estimated_revenue=revenue,
            watch_hours=watch_hours,
            impressions=impressions,
            ctr_percent=ctr,
            average_view_duration_seconds=avg_duration,
            currency=currency,
        ), warnings

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise ValueError(f"{path} is empty.")

    # Support metric,value files.
    if len(rows[0]) >= 2 and norm(rows[0][0]) in {"metric", "name"}:
        mapping = {norm(r[0]): r[1] for r in rows[1:] if len(r) >= 2}
        def metric(aliases: list[str], default: object = "") -> object:
            for alias in aliases:
                if norm(alias) in mapping:
                    return mapping[norm(alias)]
            return default
        return ChannelSummary(
            period_start=str(metric(SUMMARY_ALIASES["period_start"])),
            period_end=str(metric(SUMMARY_ALIASES["period_end"])),
            subscribers=parse_int(metric(SUMMARY_ALIASES["subscribers"])),
            views=parse_int(metric(SUMMARY_ALIASES["views"])),
            watch_hours=parse_number(metric(SUMMARY_ALIASES["watch_hours"])),
            estimated_revenue=parse_number(metric(SUMMARY_ALIASES["estimated_revenue"])),
            impressions=parse_int(metric(SUMMARY_ALIASES["impressions"])),
            ctr_percent=parse_number(metric(SUMMARY_ALIASES["ctr_percent"])),
            average_view_duration_seconds=parse_duration(metric(SUMMARY_ALIASES["average_view_duration_seconds"])),
            returning_viewers=parse_int(metric(SUMMARY_ALIASES["returning_viewers"])),
            new_viewers=parse_int(metric(SUMMARY_ALIASES["new_viewers"])),
            currency=str(metric(SUMMARY_ALIASES["currency"], currency)) or currency,
        ), warnings

    header = rows[0]
    values = rows[1] if len(rows) > 1 else []
    row = dict(zip(header, values + [""] * max(0, len(header) - len(values))))
    columns = {key: _find_column(header, aliases) for key, aliases in SUMMARY_ALIASES.items()}
    return ChannelSummary(
        period_start=str(row.get(columns["period_start"] or "", "")),
        period_end=str(row.get(columns["period_end"] or "", "")),
        subscribers=parse_int(row.get(columns["subscribers"] or "")),
        views=parse_int(row.get(columns["views"] or "")),
        watch_hours=parse_number(row.get(columns["watch_hours"] or "")),
        estimated_revenue=parse_number(row.get(columns["estimated_revenue"] or "")),
        impressions=parse_int(row.get(columns["impressions"] or "")),
        ctr_percent=parse_number(row.get(columns["ctr_percent"] or "")),
        average_view_duration_seconds=parse_duration(row.get(columns["average_view_duration_seconds"] or "")),
        returning_viewers=parse_int(row.get(columns["returning_viewers"] or "")),
        new_viewers=parse_int(row.get(columns["new_viewers"] or "")),
        currency=str(row.get(columns["currency"] or "", currency)) or currency,
    ), warnings


def apply_rights_registry(videos: list[VideoRecord], path: Path | None) -> None:
    if path is None or not path.exists():
        return
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return
        id_col = _find_column(reader.fieldnames, ["video_id", "video id", "content", "id"])
        status_col = _find_column(reader.fieldnames, ["rights_status", "rights status", "status"])
        if not id_col or not status_col:
            raise ValueError("Rights registry needs video_id and rights_status columns.")
        statuses = {
            str(row.get(id_col, "")).strip(): str(row.get(status_col, "")).strip().lower()
            for row in reader
        }
    for video in videos:
        if video.video_id in statuses and statuses[video.video_id]:
            video.rights_status = statuses[video.video_id]
