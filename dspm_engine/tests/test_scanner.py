import pytest

from dspm_engine.core.scanner import SUPPORTED_PROVIDERS, Scanner


def test_scanner_rejects_unknown_provider():
    scanner = Scanner()
    with pytest.raises(ValueError):
        scanner.scan(["aws", "unknown"])


def test_scanner_runs_all_providers():
    scanner = Scanner()
    result = scanner.scan(SUPPORTED_PROVIDERS)
    assert result.assets.buckets, "Assets should be discovered"
    assert result.lineage.to_json()["nodes"], "Lineage should contain nodes"
    assert result.risk.score >= 0
