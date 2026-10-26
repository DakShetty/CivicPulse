from backend.services.duplicate_detector import (
    haversine_distance_km,
    text_similarity_jaccard,
    evaluate_duplicate_candidate,
)


def test_haversine_distance():
    # San Francisco to Oakland is roughly 12-14 km
    sf_lat, sf_lon = 37.7749, -122.4194
    oak_lat, oak_lon = 37.8044, -122.2712
    distance = haversine_distance_km(sf_lat, sf_lon, oak_lat, oak_lon)
    assert 12.0 < distance < 16.0

    # Same location should be 0.0
    assert haversine_distance_km(sf_lat, sf_lon, sf_lat, sf_lon) == 0.0


def test_text_similarity_jaccard():
    text1 = "Deep dangerous pothole on Market Street near 5th"
    text2 = "Hazardous deep pothole located on Market Street by 5th"
    sim = text_similarity_jaccard(text1, text2)
    assert sim > 0.40

    text3 = "Completely unrelated streetlight pole damaged"
    sim_unrelated = text_similarity_jaccard(text1, text3)
    assert sim_unrelated < 0.20


def test_evaluate_duplicate_candidate():
    issue1 = {
        "title": "Severe pothole near 5th cross",
        "description": "Deep asphalt hole damaging vehicle suspensions",
        "category_id": 1,
        "latitude": 37.7750,
        "longitude": -122.4190,
    }
    issue2_duplicate = {
        "title": "Bad road pothole near 5th cross",
        "description": "Deep hole on the road damaging tires and suspensions",
        "category_id": 1,
        "latitude": 37.7752,  # ~25 meters away
        "longitude": -122.4191,
    }
    issue3_different_cat = {
        "title": "Severe streetlight failure",
        "description": "Broken light pole on road",
        "category_id": 2,  # Different category
        "latitude": 37.7750,
        "longitude": -122.4190,
    }

    res_dup = evaluate_duplicate_candidate(issue1, issue2_duplicate, max_distance_km=0.35, similarity_threshold=0.50)
    assert res_dup["is_candidate"] is True
    assert res_dup["distance_km"] < 0.1

    res_diff = evaluate_duplicate_candidate(issue1, issue3_different_cat, max_distance_km=0.35, similarity_threshold=0.50)
    assert res_diff["is_candidate"] is False
