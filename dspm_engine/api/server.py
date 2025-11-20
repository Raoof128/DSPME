"""FastAPI layer exposing DSPM results."""
from __future__ import annotations

from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from dspm_engine.core.scanner import Scanner, ScanResult

app = FastAPI(title="DSPM Engine", version="1.1.0")
scanner = Scanner()


class MisconfigurationModel(BaseModel):
    """Pydantic view of a misconfiguration finding."""

    resource: str
    provider: str
    issue: str
    severity: str
    detail: str


class PiiFindingModel(BaseModel):
    """Pydantic view of a PII finding."""

    type: str
    sample: str
    location: str
    provider: str


class RiskModel(BaseModel):
    """Response model for aggregate risk."""

    score: int
    misconfiguration_score: int
    data_score: int


class AssetModel(BaseModel):
    """Representation of a discovered storage asset."""

    name: str
    provider: str
    public: bool
    encryption: str | None
    versioning: bool
    policy: str
    region: str | None


class ScanResponse(BaseModel):
    """Structured scan response payload."""

    assets: List[AssetModel]
    pii_findings: List[PiiFindingModel]
    misconfigurations: List[MisconfigurationModel]
    lineage: dict
    risk: RiskModel

    @classmethod
    def from_result(cls, result: ScanResult) -> "ScanResponse":
        """Build a response model from a core scan result."""

        return cls(
            assets=[AssetModel(**bucket.to_dict()) for bucket in result.assets.buckets],
            pii_findings=[PiiFindingModel(**finding.__dict__) for finding in result.pii_findings],
            misconfigurations=[
                MisconfigurationModel(**finding.__dict__) for finding in result.misconfigurations
            ],
            lineage=result.lineage.to_json(),
            risk=RiskModel(**result.risk.__dict__),
        )


@app.post("/scan", response_model=ScanResponse)
def run_scan(providers: List[str] | None = None) -> ScanResponse:  # pragma: no cover
    """Execute a scan across the requested providers."""

    providers = providers or ["aws", "azure", "gcp"]
    result = scanner.scan(providers)
    return ScanResponse.from_result(result)


@app.get("/misconfigurations", response_model=List[MisconfigurationModel])
def list_misconfigurations() -> List[MisconfigurationModel]:  # pragma: no cover
    """Return current misconfiguration findings."""

    result = scanner.scan(["aws", "azure", "gcp"])
    return [MisconfigurationModel(**finding.__dict__) for finding in result.misconfigurations]


@app.get("/sensitive-data", response_model=List[PiiFindingModel])
def list_sensitive_data() -> List[PiiFindingModel]:  # pragma: no cover
    """Return current PII findings."""

    result = scanner.scan(["aws", "azure", "gcp"])
    return [PiiFindingModel(**finding.__dict__) for finding in result.pii_findings]


@app.get("/lineage")
def get_lineage() -> dict:  # pragma: no cover
    """Return lineage information in JSON form."""

    result = scanner.scan(["aws", "azure", "gcp"])
    return result.lineage.to_json()


@app.get("/risk-score", response_model=RiskModel)
def get_risk() -> RiskModel:  # pragma: no cover
    """Return aggregate risk score and contributing components."""

    result = scanner.scan(["aws", "azure", "gcp"])
    return RiskModel(**result.risk.__dict__)


@app.get("/healthz")
def healthcheck() -> dict:  # pragma: no cover
    """Liveness endpoint for container orchestration."""

    return {"status": "ok"}
