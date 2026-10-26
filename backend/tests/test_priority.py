from backend.services.priority_scorer import calculate_priority_score


def test_priority_score_base_calculation():
    # Severity 1, no hazard, no critical infra
    score, expl = calculate_priority_score(
        severity=1,
        safety_hazard=False,
        impacts_critical_infrastructure=False,
        cluster_member_count=1,
        hours_unresolved=0.0,
    )
    assert score == 7.0
    assert "Base severity level 1/5" in expl


def test_priority_score_with_safety_and_critical():
    # Severity 5 + safety hazard (+25) + critical infra (+15)
    # Severity 5 * 7 = 35 + 25 + 15 = 75
    score, expl = calculate_priority_score(
        severity=5,
        safety_hazard=True,
        impacts_critical_infrastructure=True,
        cluster_member_count=1,
        hours_unresolved=0.0,
    )
    assert score == 75.0
    assert "safety hazard" in expl.lower()
    assert "critical transit/utility" in expl.lower()


def test_priority_score_cluster_repetition_boost():
    # 3 cluster members (2 duplicates -> 2 * 3 = +6 pts)
    score1, _ = calculate_priority_score(severity=3, safety_hazard=False, impacts_critical_infrastructure=False, cluster_member_count=1)
    score3, expl = calculate_priority_score(severity=3, safety_hazard=False, impacts_critical_infrastructure=False, cluster_member_count=3)
    assert score3 == score1 + 6.0
    assert "cluster of 3" in expl


def test_priority_score_aging_unresolved():
    # 48 hours unresolved adds aging points
    score_fresh, _ = calculate_priority_score(severity=3, safety_hazard=False, impacts_critical_infrastructure=False, hours_unresolved=0)
    score_aged, expl = calculate_priority_score(severity=3, safety_hazard=False, impacts_critical_infrastructure=False, hours_unresolved=48)
    assert score_aged > score_fresh
    assert "hours" in expl
