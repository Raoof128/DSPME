from dspm_engine.core.misconfig import MisconfigurationDetector
from dspm_engine.core.storage_gcp import GcpStorageScanner


def test_misconfiguration_detector_flags_public_and_unencrypted():
    detector = MisconfigurationDetector()
    assets = GcpStorageScanner().list_buckets()
    findings = detector.evaluate_assets("gcp", assets)
    severities = {finding.severity for finding in findings}
    assert "CRITICAL" in severities  # public bucket
    assert "HIGH" in severities  # missing encryption
