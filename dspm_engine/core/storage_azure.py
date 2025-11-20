"""Azure Blob Storage scanner abstraction."""
from __future__ import annotations

from typing import Iterable, List

from .logging_utils import get_logger
from .models import StorageAsset

logger = get_logger(__name__)


class AzureStorageScanner:
    """Enumerates Blob containers with posture metadata."""

    def __init__(self, containers: Iterable[StorageAsset] | None = None) -> None:
        """Initialize the scanner with provided or sample containers."""

        self._containers = list(containers) if containers else self._sample_containers()

    def _sample_containers(self) -> List[StorageAsset]:
        """Return representative containers with demo content."""

        logger.debug("Loading sample Azure containers")
        return [
            StorageAsset(
                name="analytics-raw",
                provider="azure",
                public=False,
                encryption="MICROSOFT_MANAGED",
                versioning=True,
                policy="restricted",
                region="australiaeast",
                sample_content="Patient record: ICD-10 E11.9 diabetes, Medicare 9999 12345 1",
            ),
            StorageAsset(
                name="public-media",
                provider="azure",
                public=True,
                encryption=None,
                versioning=False,
                policy="allow-all",
                region="australiasoutheast",
                sample_content="Contact: john@example.com, Phone: 0412 345 678",
            ),
        ]

    def list_containers(self) -> List[StorageAsset]:
        logger.info("Discovered %s Azure containers", len(self._containers))
        return self._containers
