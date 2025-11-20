# API Reference

Base path: `/`

## POST /scan
Runs a multi-provider scan.

**Body**

```json
{ "providers": ["aws", "azure"] }
```

Defaults to all providers when omitted.

**Response**

```json
{
  "assets": [{"name": "finance-uploads", "provider": "aws", "public": false, ...}],
  "pii_findings": [{"type": "Medicare", "sample": "1234 56789 1", "location": "aws://..."}],
  "misconfigurations": [{"resource": "legacy-public-assets", "severity": "CRITICAL", ...}],
  "lineage": {"nodes": ["aws:finance-uploads"], "edges": [["aws:finance-uploads", "aws:legacy-public-assets"]]},
  "risk": {"score": 75, "misconfiguration_score": 60, "data_score": 15}
}
```

**Notes**

- Providers are validated; unsupported values return HTTP 422 with `{"detail": "Unsupported providers: ..."}`.
- Scans are synchronous and return all findings in a single payload for simplicity.

## GET /misconfigurations
Returns current misconfiguration findings.

## GET /sensitive-data
Returns current PII findings from sampled objects.

## GET /lineage
Returns lineage nodes and edges in JSON.

## GET /risk-score
Returns aggregate risk score breakdown.

## GET /healthz
Liveness probe.

### Error Handling

- Requests including unsupported providers return HTTP 422 with details.
- Validation errors surface as standard FastAPI error responses with `detail` and `loc` fields.
- Unexpected errors surface as HTTP 500 with minimal leak of internal details; server logs capture stack traces for diagnostics.

### Example Responses

**200 OK — Scan**

```json
{
  "assets": [
    {
      "name": "finance-uploads",
      "provider": "aws",
      "region": "ap-southeast-2",
      "encryption": true,
      "public": false,
      "versioning": true
    }
  ],
  "pii_findings": [],
  "misconfigurations": [
    {"resource": "legacy-public-assets", "severity": "CRITICAL", "description": "Bucket permits anonymous reads"}
  ],
  "lineage": {"nodes": ["aws:finance-uploads"], "edges": []},
  "risk": {"score": 72, "misconfiguration_score": 60, "data_score": 12}
}
```

**422 Unprocessable Entity — Invalid Providers**

```json
{
  "detail": "Unsupported providers: ['digital-ocean']"
}
```
