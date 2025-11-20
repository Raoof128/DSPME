"""Rule-based PII detection for Australian data classes."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from .logging_utils import get_logger
from .models import StorageAsset

logger = get_logger(__name__)


@dataclass
class PiiFinding:
    """Structured result describing a PII match."""

    type: str
    sample: str
    location: str
    provider: str


@dataclass
class PiiRule:
    """Pattern definition for detecting sensitive data."""

    name: str
    pattern: str
    description: str

    def compiled(self) -> re.Pattern[str]:
        """Return a compiled regex for the rule."""

        return re.compile(self.pattern, re.IGNORECASE)


class PiiDetector:
    """Detect PII using rule-based regex matching."""

    def __init__(self, rules: Sequence[PiiRule]):
        """Create a detector with a set of rules."""

        self.rules = list(rules)

    @classmethod
    def from_default_rules(cls) -> "PiiDetector":
        """Instantiate a detector using bundled JSON rules."""

        rule_path = Path(__file__).resolve().parent.parent / "config" / "pii_rules.json"
        rules: List[PiiRule] = []
        if rule_path.exists():
            with rule_path.open("r", encoding="utf-8") as handle:
                rule_defs = json.load(handle)
            rules = [PiiRule(**definition) for definition in rule_defs]
        else:
            logger.warning("PII rules file not found; using minimal defaults")
            rules = [
                PiiRule(
                    name="Medicare",
                    pattern=r"\b\d{4} \d{5} \d\b",
                    description="Australian Medicare number",
                ),
                PiiRule(
                    name="TFN",
                    pattern=r"\b\d{3} \d{3} \d{3}\b",
                    description="Australian Tax File Number",
                ),
            ]
        return cls(rules)

    def _content_samples(self, provider: str, assets: Iterable[StorageAsset]) -> Dict[str, str]:
        """Extract sample payloads from assets for scanning."""

        samples: Dict[str, str] = {}
        for asset in assets:
            key = f"{provider}://{asset.name}/sample.txt"
            samples[key] = asset.sample_content or ""
        return samples

    def scan_content_samples(
        self, provider: str, assets: Iterable[StorageAsset]
    ) -> List[PiiFinding]:
        """Scan provided assets for PII matches using configured rules."""

        findings: List[PiiFinding] = []
        samples = self._content_samples(provider, assets)
        for location, content in samples.items():
            for rule in self.rules:
                for match in rule.compiled().finditer(content):
                    findings.append(
                        PiiFinding(
                            type=rule.name,
                            sample=match.group(0),
                            location=location,
                            provider=provider,
                        )
                    )
        logger.info("Detected %s PII matches for provider %s", len(findings), provider)
        return findings
