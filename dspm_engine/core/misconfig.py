"""Misconfiguration detection rules for storage assets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .logging_utils import get_logger
from .models import StorageAsset

logger = get_logger(__name__)

SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@dataclass
class MisconfigurationFinding:
    """Result from evaluating a storage asset for posture gaps."""

    resource: str
    provider: str
    issue: str
    severity: str
    detail: str

    def __post_init__(self) -> None:
        """Validate severity values early for predictable ordering."""

        if self.severity not in SEVERITY_ORDER:
            raise ValueError(f"Unknown severity: {self.severity}")


class MisconfigurationDetector:
    """Evaluates storage assets for common risks."""

    def evaluate_assets(
        self, provider: str, assets: Iterable[StorageAsset]
    ) -> List[MisconfigurationFinding]:
        """Assess posture for a collection of assets.

        Args:
            provider: Cloud provider identifier.
            assets: Iterable of assets to evaluate.
        """

        findings: List[MisconfigurationFinding] = []
        for asset in assets:
            logger.debug("Evaluating posture for %s:%s", provider, asset.name)
            if asset.public:
                findings.append(
                    MisconfigurationFinding(
                        resource=asset.name,
                        provider=provider,
                        issue="Public access enabled",
                        severity="CRITICAL",
                        detail="Asset exposes data to the internet; review ACL and IAM bindings.",
                    )
                )
            if not asset.encryption:
                findings.append(
                    MisconfigurationFinding(
                        resource=asset.name,
                        provider=provider,
                        issue="Missing encryption at rest",
                        severity="HIGH",
                        detail="Enable server-side encryption with customer-managed keys.",
                    )
                )
            if not asset.versioning:
                findings.append(
                    MisconfigurationFinding(
                        resource=asset.name,
                        provider=provider,
                        issue="Versioning disabled",
                        severity="MEDIUM",
                        detail=(
                            "Versioning helps recover from ransomware and accidental overwrites."
                        ),
                    )
                )
            if asset.policy.lower() in {"allow-all", "allusers", "public"}:
                findings.append(
                    MisconfigurationFinding(
                        resource=asset.name,
                        provider=provider,
                        issue="Overly permissive policy",
                        severity="HIGH",
                        detail="Restrict bucket policies and IAM bindings to least privilege.",
                    )
                )
            if asset.tags.get("backup") == "true" and not asset.versioning:
                findings.append(
                    MisconfigurationFinding(
                        resource=asset.name,
                        provider=provider,
                        issue="Backups without immutability",
                        severity="HIGH",
                        detail="Enable versioning or object lock on backup destinations.",
                    )
                )
        return findings

    @staticmethod
    def sort_findings(findings: List[MisconfigurationFinding]) -> List[MisconfigurationFinding]:
        """Sort findings by severity for reporting."""

        severity_rank = {value: index for index, value in enumerate(SEVERITY_ORDER)}
        return sorted(
            findings,
            key=lambda finding: severity_rank.get(finding.severity, 0),
            reverse=True,
        )
