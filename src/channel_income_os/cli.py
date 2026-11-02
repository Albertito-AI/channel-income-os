from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from importlib.resources import files

from . import __version__
from .analysis import analyze
from .ingest import apply_rights_registry, load_summary, load_videos
from .reporting import write_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="channel-income-os",
        description="Turn YouTube Studio CSV exports into an evidence-led income action queue.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    analyze_parser = sub.add_parser("analyze", help="Analyze creator exports.")
    analyze_parser.add_argument("--videos", type=Path, required=True, help="Video-level CSV export.")
    analyze_parser.add_argument("--summary", type=Path, help="Optional channel summary CSV.")
    analyze_parser.add_argument("--rights", type=Path, help="Optional rights registry CSV.")
    analyze_parser.add_argument("--target", type=float, default=10000.0, help="Monthly income target.")
    analyze_parser.add_argument("--currency", default="USD", help="Currency label, for example USD or SGD.")
    analyze_parser.add_argument("--minimum-sample", type=int, default=25)
    analyze_parser.add_argument("--learning-term", action="append", default=[], help="Additional title term for the learning lane.")
    analyze_parser.add_argument("--output", type=Path, default=Path("build"))

    demo_parser = sub.add_parser("demo", help="Run the included synthetic demonstration.")
    demo_parser.add_argument("--output", type=Path, default=Path("build/demo"))
    return parser


def run_analysis(args: argparse.Namespace) -> int:
    terms = ["learning with", "explained", "case", "law", *args.learning_term]
    videos = load_videos(args.videos, terms)
    apply_rights_registry(videos, args.rights)
    summary, warnings = load_summary(args.summary, videos, args.currency)
    if not summary.currency:
        summary.currency = args.currency
    report = analyze(videos, summary, args.target, args.minimum_sample)
    outputs = write_outputs(report, warnings, args.output)
    for output in outputs:
        print(output)
    return 0


def run_demo(args: argparse.Namespace) -> int:
    sample_root = files("channel_income_os").joinpath("sample_data")
    demo_args = argparse.Namespace(
        videos=sample_root.joinpath("videos.csv"),
        summary=sample_root.joinpath("channel_summary.csv"),
        rights=sample_root.joinpath("rights_registry.csv"),
        target=10000.0,
        currency="USD",
        minimum_sample=25,
        learning_term=[],
        output=args.output,
    )
    return run_analysis(demo_args)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            return run_analysis(args)
        if args.command == "demo":
            return run_demo(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error("Unknown command.")
    return 2
