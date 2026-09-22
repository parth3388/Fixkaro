from app.seed_data import SERVICES


def test_list_services_returns_full_catalog(client):
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["services"]) == len(SERVICES)
    slugs = {s["slug"] for s in body["services"]}
    assert slugs == {s["slug"] for s in SERVICES}


def test_get_service_by_slug(client):
    response = client.get("/api/v1/services/ac-cooling")
    assert response.status_code == 200
    body = response.json()
    assert body["service"]["name"] == "AC & Cooling"


def test_get_unknown_service_returns_404(client):
    response = client.get("/api/v1/services/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert "error" in body
