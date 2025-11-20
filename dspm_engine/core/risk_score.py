"""Lightweight risk scoring model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .misconfig import SEVERITY_ORDER, MisconfigurationFinding
from .pii_detector import PiiFinding


@dataclass
class RiskBreakdown:
    """Structured risk outputs for reporting."""

    score: int
    misconfiguration_score: int
    data_score: int


class RiskAssessor:
    """Combine findings into a simple numeric risk score."""

    def calculate(
        self, pii_findings: List[PiiFinding], misconfigurations: List[MisconfigurationFinding]
    ) -> RiskBreakdown:
        """Compute combined risk given PII and misconfiguration findings."""

        misconfig_score = self._score_misconfigurations(misconfigurations)
        data_score = min(40, 10 + 5 * len(pii_findings)) if pii_findings else 0
        total = min(100, misconfig_score + data_score)
        return RiskBreakdown(
            score=total,
            misconfiguration_score=misconfig_score,
            data_score=data_score,
        )

    def _score_misconfigurations(self, misconfigurations: List[MisconfigurationFinding]) -> int:
        """Translate misconfiguration severities into a capped score."""

        severity_to_weight = {value: (index + 1) * 10 for index, value in enumerate(SEVERITY_ORDER)}
        weight = sum(severity_to_weight.get(finding.severity, 0) for finding in misconfigurations)
        return min(60, weight)
