"""GCP Cloud Storage scanner abstraction."""
from __future__ import annotations

from typing import Iterable, List

from .logging_utils import get_logger
from .models import StorageAsset

logger = get_logger(__name__)


class GcpStorageScanner:
    """Enumerates Cloud Storage buckets with metadata."""

    def __init__(self, buckets: Iterable[StorageAsset] | None = None) -> None:
        """Initialize the scanner with provided or sample buckets."""

        self._buckets = list(buckets) if buckets else self._sample_buckets()

    def _sample_buckets(self) -> List[StorageAsset]:
        """Return representative buckets with demo content."""

        logger.debug("Loading sample GCP buckets")
        return [
            StorageAsset(
                name="marketing-landing",
                provider="gcp",
                public=True,
                encryption=None,
                versioning=False,
                policy="allUsers",
                region="australia-southeast1",
                sample_content="ABN: 51824753556, Email: marketing@example.com",
            ),
            StorageAsset(
                name="backups",
                provider="gcp",
                public=False,
                encryption="CMEK",
                versioning=True,
                policy="restricted",
                region="australia-southeast2",
                sample_content="Invoice: 12345, Card: 4000 0035 6000 0008",
            ),
        ]

    def list_buckets(self) -> List[StorageAsset]:
        logger.info("Discovered %s GCP buckets", len(self._buckets))
        return self._buckets
