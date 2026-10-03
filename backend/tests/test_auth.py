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


def test_login_me_and_invalid_password(client: TestClient) -> None:
    headers = auth_headers(client, "alice")
    profile = client.get("/api/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["username"] == "alice"
    assert profile.json()["role"] == "USER"
    assert client.post("/api/auth/login", json={"username": "alice", "password": "wrong-password"}).status_code == 401


def test_protected_admin_operation_requires_token_and_admin_role(client: TestClient) -> None:
    user_headers = auth_headers(client, "driver")
    payload = {
        "slot_number": "C01", "vehicle_type": "Car", "distance_from_entrance": 20,
        "walking_distance": 20, "congestion_level": 10,
    }
    assert client.post("/api/parking/slots", json=payload).status_code == 401
    assert client.post("/api/parking/slots", json=payload, headers=user_headers).status_code == 403


def test_admin_operator_and_user_permissions(client: TestClient) -> None:
    admin_headers = auth_headers(client, "admin", "ADMIN")
    operator_headers = auth_headers(client, "operator", "PARKING_OPERATOR")
    user_headers = auth_headers(client, "driver")
    slot = client.post(
        "/api/parking/slots",
        json={"slot_number": "D01", "vehicle_type": "Car", "distance_from_entrance": 20, "walking_distance": 20, "congestion_level": 10},
        headers=admin_headers,
    ).json()
    assert client.patch(f"/api/parking/slots/{slot['id']}/status", json={"is_occupied": True}, headers=operator_headers).status_code == 200
    assert client.get("/api/ai/statistics", headers=user_headers).status_code == 403
    assert client.get("/api/ai/statistics", headers=admin_headers).status_code == 200
    assert client.get("/api/parking/active-sessions", headers=operator_headers).status_code == 200
