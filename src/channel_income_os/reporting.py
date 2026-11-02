from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any

from .utils import format_duration


def money(value: float, currency: str) -> str:
    return f"{currency} {value:,.2f}"


def write_outputs(report: dict[str, Any], warnings: list[str], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    scorecard_path = output_dir / "scorecard.json"
    queue_path = output_dir / "action_queue.csv"
    report_path = output_dir / "report.md"
    dashboard_path = output_dir / "dashboard.html"

    scorecard_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    queue = report["action_queue"]
    fieldnames = list(queue[0].keys()) if queue else []
    with queue_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(queue)

    report_path.write_text(render_markdown(report, warnings), encoding="utf-8")
    dashboard_path.write_text(render_html(report, warnings), encoding="utf-8")
    return [report_path, dashboard_path, queue_path, scorecard_path]


def render_markdown(report: dict[str, Any], warnings: list[str]) -> str:
    s = report["summary"]
    currency = report["currency"]
    required = report["views_required_at_current_rpm"]
    lines = [
        "# Channel Income OS Report",
        "",
        "## Executive reading",
        "",
        f"- Current period revenue: **{money(s['estimated_revenue'], currency)}**",
        f"- Monthly income target: **{money(report['target_monthly_income'], currency)}**",
        f"- Effective RPM: **{money(report['effective_rpm'], currency)} per 1,000 views**",
        f"- Target multiple: **{report['target_multiple']:,.1f}×**",
    ]
    if required is not None:
        lines.append(f"- Views required at the current effective RPM: **{required:,.0f}**")
    else:
        lines.append("- Views required cannot be calculated because the current effective RPM is zero.")
    lines += [
        "",
        "This is an operating analysis, not an income forecast or guarantee.",
        "",
        "## Channel baseline",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Views | {s['views']:,} |",
        f"| Watch hours | {s['watch_hours']:,.1f} |",
        f"| Estimated revenue | {money(s['estimated_revenue'], currency)} |",
        f"| Impressions | {s['impressions']:,} |",
        f"| CTR | {s['ctr_percent']:.2f}% |",
        f"| Average view duration | {format_duration(s['average_view_duration_seconds'])} |",
        f"| Subscribers | {s['subscribers']:,} |",
        "",
        "## Portfolio signals",
        "",
        f"- The supplied table contains **{report['captured_video_count']:,}** videos.",
        f"- The ten most-viewed videos produced **{report['top10_view_share']:.1%}** of captured views and **{report['top10_revenue_share']:.1%}** of captured revenue.",
        f"- Learning-lane weighted retention: **{report['learning']['retention_ratio']:.1%}**.",
        f"- Other-lane weighted retention: **{report['other']['retention_ratio']:.1%}**.",
        "",
        "## Highest-priority actions",
        "",
        "| Priority | Code | Video | Views | Retention | Revenue | Decision |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for item in report["action_queue"][:15]:
        title = item["title"].replace("|", "\\|")
        decision = item["decision"].replace("|", "\\|")
        lines.append(
            f"| {item['priority']:.0f} | {item['code']} | {title} | {item['views']:,} | "
            f"{item['retention_ratio']:.1%} | {money(item['estimated_revenue'], currency)} | {decision} |"
        )
    lines += [
        "",
        "## Revenue scenarios",
        "",
        "| Effective RPM | Views required for target |",
        "|---:|---:|",
    ]
    for scenario in report["rpm_scenarios"]:
        lines.append(f"| {money(scenario['rpm'], currency)} | {scenario['views_required']:,.0f} |")
    if warnings:
        lines += ["", "## Data warnings", ""]
        lines.extend(f"- {warning}" for warning in warnings)
    lines += [
        "",
        "## Integrity controls",
        "",
        "- Do not buy views, subscribers, comments, likes or watch time.",
        "- Separate promoted traffic from organic Browse, Suggested and Search performance.",
        "- Do not scale a video under an unresolved rights hold.",
        "- Treat high RPM on a small sample as an audit item, not a forecast.",
        "- Preserve a pre-change baseline and test one principal variable where practicable.",
    ]
    return "\n".join(lines) + "\n"


def render_html(report: dict[str, Any], warnings: list[str]) -> str:
    s = report["summary"]
    currency = report["currency"]
    required = report["views_required_at_current_rpm"]
    cards = [
        ("Period revenue", money(s["estimated_revenue"], currency)),
        ("Income target", money(report["target_monthly_income"], currency)),
        ("Effective RPM", money(report["effective_rpm"], currency)),
        ("Target multiple", f"{report['target_multiple']:,.1f}×"),
        ("Views", f"{s['views']:,}"),
        ("Views needed", f"{required:,.0f}" if required is not None else "n/a"),
    ]
    rows = []
    for item in report["action_queue"][:20]:
        rows.append(
            "<tr>"
            f"<td>{item['priority']:.0f}</td>"
            f"<td><span class='badge'>{html.escape(item['code'])}</span></td>"
            f"<td>{html.escape(item['title'])}<br><small>{html.escape(item['video_id'])}</small></td>"
            f"<td>{item['views']:,}</td>"
            f"<td>{item['retention_ratio']:.1%}</td>"
            f"<td>{html.escape(money(item['estimated_revenue'], currency))}</td>"
            f"<td>{html.escape(item['decision'])}</td>"
            "</tr>"
        )
    warning_html = "".join(f"<li>{html.escape(w)}</li>" for w in warnings) or "<li>No ingestion warnings.</li>"
    cards_html = "".join(
        f"<div class='card'><div class='label'>{html.escape(label)}</div><div class='value'>{html.escape(value)}</div></div>"
        for label, value in cards
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Channel Income OS</title>
<style>
:root {{ color-scheme: light dark; --bg:#0b1020; --panel:#141b2d; --text:#eef2ff; --muted:#a8b2d1; --line:#2a3552; --accent:#7dd3fc; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter, ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--text); }}
main {{ max-width:1180px; margin:auto; padding:32px 20px 64px; }}
h1 {{ margin-bottom:4px; }} p, li {{ color:var(--muted); line-height:1.6; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:14px; margin:24px 0; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:18px; }}
.label {{ color:var(--muted); font-size:.85rem; }} .value {{ font-size:1.55rem; font-weight:750; margin-top:8px; }}
.tablewrap {{ overflow:auto; border:1px solid var(--line); border-radius:14px; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); font-size:.92rem; }}
th,td {{ padding:12px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
th {{ position:sticky; top:0; background:#18213a; }} small {{ color:var(--muted); }}
.badge {{ display:inline-block; padding:3px 7px; border-radius:999px; background:#20304e; color:var(--accent); white-space:nowrap; }}
.notice {{ border-left:4px solid var(--accent); padding:4px 16px; margin:20px 0; }}
footer {{ margin-top:32px; color:var(--muted); font-size:.85rem; }}
</style>
</head>
<body><main>
<h1>Channel Income OS</h1>
<p>API-free, local analysis of YouTube Studio exports.</p>
<div class="notice"><strong>Decision rule:</strong> maximise qualified viewing and verified net income, not vanity metrics.</div>
<div class="grid">{cards_html}</div>
<h2>Priority action queue</h2>
<div class="tablewrap"><table>
<thead><tr><th>Pri.</th><th>Signal</th><th>Video</th><th>Views</th><th>Retention</th><th>Revenue</th><th>Decision</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table></div>
<h2>Data warnings</h2><ul>{warning_html}</ul>
<footer>Generated locally. No telemetry. No income guarantee. Not affiliated with YouTube or Google.</footer>
</main></body></html>"""
