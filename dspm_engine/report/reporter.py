"""Reporting utilities for DSPM findings."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from jinja2 import Environment, FileSystemLoader, select_autoescape

from dspm_engine.core.misconfig import MisconfigurationDetector
from dspm_engine.core.scanner import ScanResult

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def _jinja_env() -> Environment:
    """Construct a Jinja environment rooted at the templates directory."""

    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )


class Reporter:
    """Generate Markdown or JSON reports from scan results."""

    def __init__(self) -> None:
        """Create a reporter with preconfigured Jinja environment."""

        self.env = _jinja_env()

    def render(self, result: ScanResult, fmt: Literal["markdown", "json"]) -> str:
        """Render a scan result to the requested format."""

        if fmt == "json":
            return json.dumps(
                {
                    "assets": result.assets.to_dict()["buckets"],
                    "pii_findings": [asdict(finding) for finding in result.pii_findings],
                    "misconfigurations": [asdict(finding) for finding in result.misconfigurations],
                    "lineage": result.lineage.to_json(),
                    "risk": asdict(result.risk),
                },
                indent=2,
            )
        template = self.env.get_template("report.md.j2")
        sorted_findings = MisconfigurationDetector.sort_findings(result.misconfigurations)
        return template.render(result=result, misconfigurations=sorted_findings)
