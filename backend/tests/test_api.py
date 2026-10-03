from fastapi.testclient import TestClient


def auth_headers(client: TestClient, username: str, role: str = "USER") -> dict[str, str]:
    password = "secure-password"
    registration = client.post(
        "/api/auth/register",
        json={"username": username, "email": f"{username}@smartpark.test", "password": password, "role": role},
    )
    assert registration.status_code == 201
    login = client.post("/api/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def slot_payload(slot_number: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "slot_number": slot_number,
        "floor": "G",
        "zone": "A",
        "slot_type": "Normal",
        "vehicle_type": "Car",
        "is_ev": False,
        "is_accessible": False,
        "distance_from_entrance": 30,
        "walking_distance": 30,
        "congestion_level": 10,
    }
    payload.update(overrides)
    return payload


def create_slot(client: TestClient, headers: dict[str, str], slot_number: str, **overrides: object) -> dict[str, object]:
    response = client.post("/api/parking/slots", json=slot_payload(slot_number, **overrides), headers=headers)
    assert response.status_code == 201
    return response.json()


def test_parking_slot_crud(client: TestClient) -> None:
    admin_headers = auth_headers(client, "admin", "ADMIN")
    user_headers = auth_headers(client, "driver")
    created = create_slot(client, admin_headers, "A12")
    slot_id = created["id"]

    assert client.get("/api/parking/slots", headers=user_headers).json()[0]["slot_number"] == "A12"
    assert client.get(f"/api/parking/slots/{slot_id}", headers=user_headers).status_code == 200
    updated = client.put(f"/api/parking/slots/{slot_id}", json={"congestion_level": 25}, headers=admin_headers)
    assert updated.status_code == 200
    assert updated.json()["congestion_level"] == 25
    assert client.delete(f"/api/parking/slots/{slot_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/api/parking/slots/{slot_id}", headers=user_headers).status_code == 404


def test_recommendation_filters_and_ranks_top_three(client: TestClient) -> None:
    admin_headers = auth_headers(client, "admin", "ADMIN")
    user_headers = auth_headers(client, "driver")
    create_slot(client, admin_headers, "A01", distance_from_entrance=20, walking_distance=20, congestion_level=95)
    create_slot(client, admin_headers, "A02", distance_from_entrance=70, walking_distance=40, congestion_level=10)
    create_slot(client, admin_headers, "A03", vehicle_type="SUV")
    create_slot(client, admin_headers, "A04", is_occupied=True)
    create_slot(client, admin_headers, "A05", distance_from_entrance=120, walking_distance=110, congestion_level=20)

    response = client.post("/api/parking/recommend", json={"vehicle_type": "Car", "priority": 50}, headers=user_headers)

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert len(recommendations) == 3
    assert recommendations[0]["slot"] == "A02"
    assert all(item["slot"] not in {"A03", "A04"} for item in recommendations)
    assert "membership_values" in recommendations[0]["factors"]


def test_allocate_then_release_changes_slot_and_session_state(client: TestClient) -> None:
    admin_headers = auth_headers(client, "admin", "ADMIN")
    user_headers = auth_headers(client, "driver")
    slot = create_slot(client, admin_headers, "B01")
    allocation = client.post(
        "/api/parking/allocate",
        json={"selected_slot_id": slot["id"], "vehicle_type": "Car", "priority": 80},
        headers=user_headers,
    )
    assert allocation.status_code == 200
    assert allocation.json()["status"] == "allocated"
    assert client.get(f"/api/parking/slots/{slot['id']}", headers=user_headers).json()["is_occupied"] is True
    assert client.post("/api/parking/allocate", json={"selected_slot_id": slot["id"], "vehicle_type": "Car"}, headers=user_headers).status_code == 409

    released = client.post("/api/parking/release", json={"slot_id": slot["id"]}, headers=user_headers)
    assert released.status_code == 200
    assert released.json()["status"] == "released"
    assert client.get(f"/api/parking/slots/{slot['id']}", headers=user_headers).json()["is_occupied"] is False


def test_ai_score_rules_statistics_and_openapi(client: TestClient) -> None:
    admin_headers = auth_headers(client, "admin", "ADMIN")
    score = client.post(
        "/api/ai/calculate-score",
        json={"distance": 20, "congestion": 10, "compatibility": 95, "walking_distance": 20, "priority": 85},
    )
    assert score.status_code == 200
    assert score.json()["score"] == 85.04
    assert len(client.get("/api/ai/rules").json()["rules"]) == 12
    assert client.get("/api/ai/statistics", headers=admin_headers).json()["total_slots"] == 0
    schema = client.get("/openapi.json").json()
    assert "/api/parking/recommend" in schema["paths"]
    assert "/api/ai/calculate-score" in schema["paths"]
    assert client.get("/docs").status_code == 200
