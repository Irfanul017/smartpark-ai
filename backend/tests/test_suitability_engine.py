import pytest

from app.ai.suitability_engine import calculate_parking_suitability


def _score(**overrides: float) -> dict[str, object]:
    values = {"distance": 20, "congestion": 10, "compatibility": 95, "walking_distance": 20, "priority": 85}
    values.update(overrides)
    return calculate_parking_suitability(**values)


def test_near_low_congestion_and_excellent_compatibility_is_highly_suitable() -> None:
    result = _score()
    assert result["score"] >= 85
    assert result["category"] in {"HIGH", "VERY_HIGH"}
    assert any(rule["id"] == "R1" for rule in result["activated_rules"])


def test_far_high_congestion_activates_low_suitability_rule() -> None:
    result = _score(distance=180, congestion=90, compatibility=60, walking_distance=180, priority=20)
    assert result["score"] <= 45
    assert any(rule["id"] == "R3" for rule in result["activated_rules"])


def test_poor_compatibility_produces_very_low_suitability() -> None:
    result = _score(distance=150, congestion=50, compatibility=10, walking_distance=150, priority=50)
    assert result["score"] <= 25
    assert any(rule["id"] == "R4" for rule in result["activated_rules"])


def test_short_walking_distance_and_low_congestion_activate_rule_six() -> None:
    result = _score(walking_distance=15, congestion=10, priority=50, compatibility=60)
    assert any(rule["id"] == "R6" for rule in result["activated_rules"])
    assert result["score"] >= 65


def test_high_priority_and_excellent_compatibility_activate_rule_eight() -> None:
    result = _score(distance=140, congestion=50, walking_distance=140, priority=90)
    assert any(rule["id"] == "R8" for rule in result["activated_rules"])
    assert result["score"] >= 85


@pytest.mark.parametrize("values", [
    {"distance": 0, "congestion": 0, "compatibility": 0, "walking_distance": 0, "priority": 0},
    {"distance": 200, "congestion": 100, "compatibility": 100, "walking_distance": 200, "priority": 100},
    {"distance": 100, "congestion": 50, "compatibility": 50, "walking_distance": 100, "priority": 50},
])
def test_boundary_and_middle_values_always_produce_a_valid_score(values: dict[str, float]) -> None:
    result = calculate_parking_suitability(**values)
    assert 0 <= result["score"] <= 100
    assert result["category"] in {"VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"}


@pytest.mark.parametrize("field,value", [
    ("distance", -1), ("distance", 201), ("congestion", 101),
    ("compatibility", "excellent"), ("walking_distance", float("inf")), ("priority", True),
])
def test_invalid_values_raise_value_error(field: str, value: object) -> None:
    values: dict[str, object] = {"distance": 20, "congestion": 20, "compatibility": 90, "walking_distance": 20, "priority": 80}
    values[field] = value
    with pytest.raises(ValueError):
        calculate_parking_suitability(**values)  # type: ignore[arg-type]
