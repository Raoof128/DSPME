"""Lightweight AWS storage scanner abstraction."""
from __future__ import annotations

from typing import Iterable, List

from .logging_utils import get_logger
from .models import StorageAsset

logger = get_logger(__name__)


class AwsStorageScanner:
    """Discovers S3 buckets and posture metadata.

    This implementation returns curated sample data suitable for offline testing.
    Replace :meth:`_sample_buckets` with boto3-backed discovery for production use.
    """

    def __init__(self, buckets: Iterable[StorageAsset] | None = None) -> None:
        """Initialize the scanner with provided or sample buckets."""

        self._buckets = list(buckets) if buckets else self._sample_buckets()

    def _sample_buckets(self) -> List[StorageAsset]:
        """Return representative sample buckets with content for demos."""

        logger.debug("Loading sample AWS buckets")
        return [
            StorageAsset(
                name="finance-uploads",
                provider="aws",
                public=False,
                encryption="AES256",
                versioning=True,
                policy="restricted",
                region="ap-southeast-2",
                sample_content=(
                    "Customer: Jane Doe, DOB: 1988-01-01, Medicare: 1234 56789 1, TFN: 123 456 789"
                ),
            ),
            StorageAsset(
                name="legacy-public-assets",
                provider="aws",
                public=True,
                encryption=None,
                versioning=False,
                policy="allow-all",
                region="ap-southeast-2",
                sample_content="CC: 4111 1111 1111 1111, BSB: 123-456 Account: 12345678",
            ),
        ]

    def list_buckets(self) -> List[StorageAsset]:
        """Return discovered buckets with posture metadata."""

        logger.info("Discovered %s AWS buckets", len(self._buckets))
        return self._buckets
