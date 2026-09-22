from app.models.customer import Customer


def test_create_booking_success(client, valid_booking_payload):
    response = client.post("/api/v1/bookings", json=valid_booking_payload)
    assert response.status_code == 201

    body = response.json()
    assert body["success"] is True
    booking = body["booking"]
    assert booking["booking_reference"].startswith("FIX-")
    assert booking["status"] == "PENDING"
    assert booking["service"]["name"] == "AC & Cooling"
    assert booking["customer_name"] == "Ravi Kumar"
    # Phone/email must never be echoed back.
    assert "phone" not in booking
    assert "email" not in booking


def test_create_booking_normalises_phone_formats(client, valid_booking_payload):
    valid_booking_payload["phone"] = "+91 88242-76600"
    response = client.post("/api/v1/bookings", json=valid_booking_payload)
    assert response.status_code == 201


def test_create_booking_missing_required_field_returns_422(client, valid_booking_payload):
    del valid_booking_payload["full_name"]
    response = client.post("/api/v1/bookings", json=valid_booking_payload)
    assert response.status_code == 422
    assert response.json()["success"] is False


def test_create_booking_invalid_phone_returns_422(client, valid_booking_payload):
    valid_booking_payload["phone"] = "12345"
    response = client.post("/api/v1/bookings", json=valid_booking_payload)
    assert response.status_code == 422


def test_create_booking_short_message_returns_422(client, valid_booking_payload):
    valid_booking_payload["message"] = "hi"
    response = client.post("/api/v1/bookings", json=valid_booking_payload)
    assert response.status_code == 422


def test_create_booking_unknown_service_returns_400(client, valid_booking_payload):
    valid_booking_payload["service"] = "Rocket Repair"
    response = client.post("/api/v1/bookings", json=valid_booking_payload)
    assert response.status_code == 400
    assert response.json()["success"] is False


def test_create_booking_service_match_is_case_insensitive(client, valid_booking_payload):
    valid_booking_payload["service"] = "ac & cooling"
    response = client.post("/api/v1/bookings", json=valid_booking_payload)
    assert response.status_code == 201


def test_repeat_phone_reuses_same_customer_record(client, valid_booking_payload, db_session):
    client.post("/api/v1/bookings", json=valid_booking_payload)
    valid_booking_payload["full_name"] = "Ravi K."  # updated name on second visit
    client.post("/api/v1/bookings", json=valid_booking_payload)

    customers = db_session.query(Customer).filter(Customer.phone == "8824276600").all()
    assert len(customers) == 1
    assert customers[0].full_name == "Ravi K."


def test_get_booking_with_correct_phone(client, valid_booking_payload):
    create_resp = client.post("/api/v1/bookings", json=valid_booking_payload)
    reference = create_resp.json()["booking"]["booking_reference"]

    response = client.get(f"/api/v1/bookings/{reference}", params={"phone": "8824276600"})
    assert response.status_code == 200
    assert response.json()["booking"]["booking_reference"] == reference


def test_get_booking_with_wrong_phone_returns_404(client, valid_booking_payload):
    create_resp = client.post("/api/v1/bookings", json=valid_booking_payload)
    reference = create_resp.json()["booking"]["booking_reference"]

    response = client.get(f"/api/v1/bookings/{reference}", params={"phone": "9999999999"})
    assert response.status_code == 404
    assert response.json()["success"] is False


def test_get_nonexistent_booking_reference_returns_404(client):
    response = client.get("/api/v1/bookings/FIX-DOESNOTEX", params={"phone": "8824276600"})
    assert response.status_code == 404


def test_cancel_booking_success(client, valid_booking_payload):
    create_resp = client.post("/api/v1/bookings", json=valid_booking_payload)
    reference = create_resp.json()["booking"]["booking_reference"]

    response = client.post(f"/api/v1/bookings/{reference}/cancel", json={"phone": "8824276600"})
    assert response.status_code == 200
    assert response.json()["booking"]["status"] == "CANCELLED"


def test_cancel_booking_wrong_phone_returns_404(client, valid_booking_payload):
    create_resp = client.post("/api/v1/bookings", json=valid_booking_payload)
    reference = create_resp.json()["booking"]["booking_reference"]

    response = client.post(f"/api/v1/bookings/{reference}/cancel", json={"phone": "9999999999"})
    assert response.status_code == 404


def test_cancel_already_cancelled_booking_returns_409(client, valid_booking_payload):
    create_resp = client.post("/api/v1/bookings", json=valid_booking_payload)
    reference = create_resp.json()["booking"]["booking_reference"]

    client.post(f"/api/v1/bookings/{reference}/cancel", json={"phone": "8824276600"})
    response = client.post(f"/api/v1/bookings/{reference}/cancel", json={"phone": "8824276600"})
    assert response.status_code == 409
    assert response.json()["success"] is False


def test_cancelled_booking_status_persists_on_lookup(client, valid_booking_payload):
    create_resp = client.post("/api/v1/bookings", json=valid_booking_payload)
    reference = create_resp.json()["booking"]["booking_reference"]
    client.post(f"/api/v1/bookings/{reference}/cancel", json={"phone": "8824276600"})

    response = client.get(f"/api/v1/bookings/{reference}", params={"phone": "8824276600"})
    assert response.json()["booking"]["status"] == "CANCELLED"
