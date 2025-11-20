"""Core dataclasses and type helpers for DSPM components."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Literal, Optional

Provider = Literal["aws", "azure", "gcp"]


@dataclass
class StorageAsset:
    """Normalized representation of a cloud storage asset."""

    name: str
    provider: Provider
    public: bool = False
    encryption: Optional[str] = None
    versioning: bool = True
    policy: str = "restricted"
    region: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    sample_content: Optional[str] = None

    def __post_init__(self) -> None:
        """Normalize booleans and casing for consistent downstream usage."""

        self.public = bool(self.public)
        self.versioning = bool(self.versioning)
        if self.encryption:
            self.encryption = self.encryption.upper()
        self.policy = self.policy or "restricted"

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "StorageAsset":
        """Create a :class:`StorageAsset` from a raw mapping."""

        return cls(
            name=payload.get("name", "unknown"),
            provider=payload.get("provider", "aws"),
            public=_coerce_bool(payload.get("public", False)),
            encryption=payload.get("encryption"),
            versioning=_coerce_bool(payload.get("versioning", True)),
            policy=payload.get("policy", "restricted"),
            region=payload.get("region"),
            tags=payload.get("tags", {}),
            sample_content=payload.get("sample_content"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the asset into a dictionary for JSON rendering."""

        return asdict(self)


@dataclass
class AssetInventory:
    """Represents discovered storage assets across providers."""

    buckets: List[StorageAsset] = field(default_factory=list)

    def add(self, assets: Iterable[StorageAsset]) -> None:
        """Append discovered assets to the inventory."""

        self.buckets.extend(list(assets))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the inventory into a dictionary."""

        return {"buckets": [bucket.to_dict() for bucket in self.buckets]}


def _coerce_bool(value: Any) -> bool:
    """Convert loosely-typed truthy values into booleans."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"true", "yes", "1", "public", "allusers"}
    return bool(value)
