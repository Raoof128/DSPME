# DSPM Engine Architecture

## Overview

The engine models a full DSPM control-plane spanning discovery, classification, posture analysis, lineage, and reporting. It uses provider abstractions to keep the core logic credential-agnostic while enabling real SDK integrations.

## Components

- **Models** (`dspm_engine/core/models.py`): shared dataclasses for normalized storage assets and inventories.
- **Storage scanners** (`dspm_engine/core/storage_*.py`): Enumerate buckets/containers and collect posture metadata.
- **Misconfiguration detector** (`dspm_engine/core/misconfig.py`): Applies rules for public exposure, encryption, versioning, and policy health.
- **PII detector** (`dspm_engine/core/pii_detector.py`): Regex-based detection for AU identifiers and financial tokens.
- **Lineage graph** (`dspm_engine/core/lineage.py`): Builds directed graphs to represent data movement and exports Mermaid/JSON.
- **Risk scorer** (`dspm_engine/core/risk_score.py`): Blends misconfiguration severity and data findings into a 0–100 score.
- **Reporting** (`dspm_engine/report/`): Jinja2 templates for Markdown/JSON outputs.
- **Interfaces**: CLI (`dspm_engine/cli/dspmctl.py`) and API (`dspm_engine/api/server.py`).

## Data Flow

1. **Scan orchestration** via `Scanner.scan()` triggers provider enumerations.
2. **Posture evaluation** checks misconfigurations and samples content for PII detection.
3. **Lineage graph** links assets within each provider for quick visualization.
4. **Risk scoring** aggregates findings into actionable metrics.
5. **Reporting** renders Markdown/JSON for stakeholders.

## Layering and Clean Architecture

- **Interface layer**: FastAPI (`dspm_engine/api`) and CLI (`dspm_engine/cli`) expose stable entry points and map inputs to core use cases.
- **Application services**: `Scanner` coordinates provider discovery, detection, lineage, and scoring without infrastructure knowledge.
- **Domain logic**: PII detection, misconfiguration rules, lineage graphing, and risk scoring live under `dspm_engine/core` with type-safe models.
- **Presentation**: `dspm_engine/report` renders results using Jinja2 templates for Markdown/JSON deliverables.

## Operational Considerations

- **Configuration** is provided via YAML/JSON under `dspm_engine/config`, enabling provider toggles and rule extension without code changes.
- **Logging** is centralized in `dspm_engine/core/logging_utils.py` and defaults to INFO with environment overrides.
- **Error handling**: invalid provider requests raise `ValueError`, while missing rule files fall back to safe defaults with warnings.
- **Extensibility**: replace sample discovery methods with SDK-backed implementations; add lineage exporters or detectors without modifying callers thanks to shared models.

## Deployment Patterns

- **Local development**: run the CLI or start FastAPI with `uvicorn dspm_engine.api.server:app --reload`.
- **Containerized**: use `Dockerfile` or `docker-compose.yml` to run the API with pinned dependencies.
- **CI/CD**: `.github/workflows/ci.yml` executes linting and tests; extend with security scans (Bandit, pip-audit) as needed.

## Extensibility

- Replace `_sample_buckets` and `_sample_containers` with real SDK calls.
- Extend `pii_rules.json` with additional regex rules or plug-in ML classifiers.
- Add new exporters in `LineageGraph` for DOT/GraphML.
- Integrate CI by running `ruff` and `pytest` in pipelines.
