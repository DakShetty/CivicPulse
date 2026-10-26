import math
import re
from datetime import datetime, timezone


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    radius_earth_km = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return radius_earth_km * c


def tokenize_text(text: str) -> set[str]:
    """Extracts normalized words of length >= 3."""
    words = re.findall(r"\b[a-zA-Z0-9]{3,}\b", (text or "").lower())
    # Exclude common stopwords
    stopwords = {"the", "and", "this", "that", "with", "from", "for", "are", "have", "been", "near", "there"}
    return {w for w in words if w not in stopwords}


def text_similarity_jaccard(text1: str, text2: str) -> float:
    """Computes Jaccard index between word sets."""
    tokens1 = tokenize_text(text1)
    tokens2 = tokenize_text(text2)
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    return intersection / union if union > 0 else 0.0


def evaluate_duplicate_candidate(
    new_issue_dict: dict,
    existing_issue_dict: dict,
    max_distance_km: float = 0.35,
    similarity_threshold: float = 0.50,
) -> dict:
    """Evaluates whether two issues represent a potential duplicate pair.
    
    Returns a dictionary with:
    - is_candidate (bool)
    - distance_km (float)
    - text_similarity (float)
    - composite_similarity (float)
    - explanation (str)
    """
    lat1, lon1 = new_issue_dict["latitude"], new_issue_dict["longitude"]
    lat2, lon2 = existing_issue_dict["latitude"], existing_issue_dict["longitude"]

    distance = haversine_distance_km(lat1, lon1, lat2, lon2)
    same_category = new_issue_dict["category_id"] == existing_issue_dict["category_id"]

    combined_text1 = f"{new_issue_dict.get('title', '')} {new_issue_dict.get('description', '')}"
    combined_text2 = f"{existing_issue_dict.get('title', '')} {existing_issue_dict.get('description', '')}"
    text_sim = text_similarity_jaccard(combined_text1, combined_text2)

    # Spatial score: 1.0 at 0m distance, decaying down to 0 at max_distance_km
    spatial_score = max(0.0, 1.0 - (distance / max_distance_km)) if distance <= max_distance_km else 0.0

    # Composite similarity calculation:
    # 40% spatial proximity, 40% text description overlap, 20% category match
    category_score = 1.0 if same_category else 0.0
    composite_similarity = (spatial_score * 0.40) + (text_sim * 0.40) + (category_score * 0.20)

    # Must be within distance limit AND match category AND meet composite threshold
    is_candidate = (distance <= max_distance_km) and same_category and (composite_similarity >= similarity_threshold)

    distance_m = int(distance * 1000)
    explanation = (
        f"Located {distance_m}m apart (threshold <= {int(max_distance_km * 1000)}m); "
        f"{'Same category' if same_category else 'Different category'}; "
        f"Text similarity {int(text_sim * 100)}%; "
        f"Overall match score: {int(composite_similarity * 100)}%"
    )

    return {
        "is_candidate": is_candidate,
        "distance_km": round(distance, 4),
        "text_similarity": round(text_sim, 3),
        "composite_similarity": round(composite_similarity, 3),
        "explanation": explanation,
    }
