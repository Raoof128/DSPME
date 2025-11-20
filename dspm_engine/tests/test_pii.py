from dspm_engine.core.pii_detector import PiiDetector
from dspm_engine.core.storage_aws import AwsStorageScanner


def test_pii_detection_matches_default_rules():
    detector = PiiDetector.from_default_rules()
    assets = AwsStorageScanner().list_buckets()
    findings = detector.scan_content_samples("aws", assets)
    types = {f.type for f in findings}
    assert "Medicare" in types
    assert "TFN" in types
