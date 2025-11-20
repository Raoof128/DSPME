"""Command-line interface for the DSPM engine."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from dspm_engine.core.logging_utils import setup_logging
from dspm_engine.core.scanner import Scanner
from dspm_engine.report.reporter import Reporter


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for DSPM operations."""

    parser = argparse.ArgumentParser(description="DSPM Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Run scans against providers")
    scan_parser.add_argument(
        "providers", nargs="*", default=["aws", "azure", "gcp"], help="Provider list"
    )

    report_parser = subparsers.add_parser("report", help="Generate reports from a new scan")
    report_parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    report_parser.add_argument("--output", type=Path, default=Path("dspm_report.md"))

    return parser.parse_args()


def run_scan(providers: Iterable[str]) -> Scanner:
    """Execute a scan and print risk summary."""

    scanner = Scanner()
    result = scanner.scan(providers)
    print(json.dumps(result.risk.__dict__, indent=2))
    return scanner


def main() -> None:  # pragma: no cover - CLI wrapper
    """Entry point for the ``dspmctl`` CLI."""

    setup_logging()
    args = parse_args()
    if args.command == "scan":
        run_scan(args.providers)
    elif args.command == "report":
        scanner = Scanner()
        result = scanner.scan(["aws", "azure", "gcp"])
        reporter = Reporter()
        rendered = reporter.render(result, fmt=args.format)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Report written to {args.output}")


if __name__ == "__main__":  # pragma: no cover
    main()
