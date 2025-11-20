"""Orchestration layer for DSPM scans."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .lineage import LineageGraph
from .logging_utils import get_logger
from .misconfig import MisconfigurationDetector, MisconfigurationFinding
from .models import AssetInventory, StorageAsset
from .pii_detector import PiiDetector, PiiFinding
from .risk_score import RiskAssessor, RiskBreakdown
from .storage_aws import AwsStorageScanner
from .storage_azure import AzureStorageScanner
from .storage_gcp import GcpStorageScanner

logger = get_logger(__name__)
SUPPORTED_PROVIDERS = {"aws", "azure", "gcp"}


@dataclass
class ScanResult:
    """Aggregated results from a DSPM scan."""

    assets: AssetInventory
    pii_findings: List[PiiFinding]
    misconfigurations: List[MisconfigurationFinding]
    lineage: LineageGraph
    risk: RiskBreakdown


class Scanner:
    """High-level scanner that coordinates provider-specific modules."""

    def __init__(
        self,
        pii_detector: Optional[PiiDetector] = None,
        misconfig_detector: Optional[MisconfigurationDetector] = None,
        risk_assessor: Optional[RiskAssessor] = None,
    ) -> None:
        """Create a scanner with optional dependency overrides."""

        self.pii_detector = pii_detector or PiiDetector.from_default_rules()
        self.misconfig_detector = misconfig_detector or MisconfigurationDetector()
        self.risk_assessor = risk_assessor or RiskAssessor()
        self.lineage_graph = LineageGraph()

    def _scan_provider(self, provider: str) -> Iterable[StorageAsset]:
        """Route provider-specific discovery to the correct scanner."""

        if provider == "aws":
            return AwsStorageScanner().list_buckets()
        if provider == "azure":
            return AzureStorageScanner().list_containers()
        if provider == "gcp":
            return GcpStorageScanner().list_buckets()
        raise ValueError(f"Unsupported provider: {provider}")

    def scan(self, providers: Iterable[str]) -> ScanResult:
        """Run DSPM scans across the given providers."""

        provider_set = {provider.lower() for provider in providers}
        unsupported = provider_set - SUPPORTED_PROVIDERS
        if unsupported:
            raise ValueError(f"Unsupported providers requested: {sorted(unsupported)}")

        assets = AssetInventory()
        pii_findings: List[PiiFinding] = []
        misconfigurations: List[MisconfigurationFinding] = []

        for provider in providers:
            logger.info("Scanning provider %s", provider)
            discovered_assets = list(self._scan_provider(provider))
            assets.add(discovered_assets)
            misconfigurations.extend(
                self.misconfig_detector.evaluate_assets(provider, discovered_assets)
            )
            pii_findings.extend(
                self.pii_detector.scan_content_samples(provider, discovered_assets)
            )
            self.lineage_graph.add_provider_assets(provider, discovered_assets)

        risk = self.risk_assessor.calculate(pii_findings, misconfigurations)
        return ScanResult(
            assets=assets,
            pii_findings=pii_findings,
            misconfigurations=misconfigurations,
            lineage=self.lineage_graph,
            risk=risk,
        )
