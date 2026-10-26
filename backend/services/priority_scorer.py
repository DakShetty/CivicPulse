from datetime import datetime, timezone


def calculate_priority_score(
    severity: int,
    safety_hazard: bool,
    impacts_critical_infrastructure: bool,
    cluster_member_count: int = 1,
    hours_unresolved: float = 0.0,
    category_weight: float = 1.0,
) -> tuple[float, str]:
    """Calculates an explainable priority score between 0 and 100.
    
    Formula components:
    - Base severity (1-5): up to 35 points
    - Safety hazard bonus: +25 points
    - Critical infrastructure impact: +15 points
    - Cluster repetition factor (similar reports): up to +15 points
    - Time-aging unresolved factor: up to +10 points
    Scaled by category default severity weight.
    """
    # 1. Base severity component (7 points per level, 1-5 -> 7 to 35 pts)
    clamped_severity = max(1, min(5, int(severity)))
    severity_pts = clamped_severity * 7.0

    # 2. Safety hazard
    safety_pts = 25.0 if safety_hazard else 0.0

    # 3. Critical infrastructure
    critical_pts = 15.0 if impacts_critical_infrastructure else 0.0

    # 4. Cluster repetition factor (each duplicate adds 3 pts, up to 15 max)
    duplicates = max(0, cluster_member_count - 1)
    cluster_pts = min(15.0, duplicates * 3.0)

    # 5. Unresolved aging factor (after 24h, adds 1 pt every 24h up to 10 max)
    aging_pts = min(10.0, max(0.0, (hours_unresolved / 24.0) * 1.5))

    raw_score = (severity_pts + safety_pts + critical_pts + cluster_pts + aging_pts) * category_weight
    final_score = round(max(0.0, min(100.0, raw_score)), 1)

    # Build human-readable explainable rationale
    reasons = [f"Base severity level {clamped_severity}/5 (+{severity_pts:.0f} pts)"]
    if safety_hazard:
        reasons.append("Reported as direct public safety hazard (+25 pts)")
    if impacts_critical_infrastructure:
        reasons.append("Affects critical transit/utility access (+15 pts)")
    if cluster_member_count > 1:
        reasons.append(f"Confirmed/linked in a cluster of {cluster_member_count} reports (+{cluster_pts:.0f} pts)")
    if hours_unresolved >= 24:
        reasons.append(f"Unresolved for {hours_unresolved:.1f} hours (+{aging_pts:.1f} pts aging)")
    if category_weight != 1.0:
        reasons.append(f"Category weight multiplier x{category_weight:.2f}")

    explanation = "; ".join(reasons)
    return final_score, explanation
