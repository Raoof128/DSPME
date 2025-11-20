# Security Policy

## Reporting

Please report suspected vulnerabilities confidentially to `security@example.com`. We aim to acknowledge within 2 business days and provide a mitigation path or patch within 14 days.

## Supported Versions

This project is a reference implementation. The `main` branch receives fixes; no LTS branches are provided.

## Hardening Guidance

- Use least-privilege IAM roles for storage enumeration.
- Enforce encryption at rest (SSE-KMS, CMK, CMEK) and TLS in transit.
- Disable public ACLs and prefer block-public-access controls.
- Enable audit logging (S3 server access logs, Azure Storage logging, GCP Storage Insights).
- Configure lifecycle and versioning to protect against ransomware.
