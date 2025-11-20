from dspm_engine.core.misconfig import MisconfigurationFinding
from dspm_engine.core.risk_score import RiskAssessor


def test_risk_assessor_caps_scores():
    assessor = RiskAssessor()
    misconfigs = [
        MisconfigurationFinding(
            resource="bucket", provider="aws", issue="public", severity="CRITICAL", detail=""
        )
        for _ in range(10)
    ]
    result = assessor.calculate([], misconfigs)
    assert result.misconfiguration_score <= 60
    assert result.score == result.misconfiguration_score
