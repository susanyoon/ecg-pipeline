from fastapi.testclient import TestClient

from ecg.api import app

client = TestClient(app)


def test_root():
    assert client.get("/").status_code == 200


def test_recordings_endpoint():
    response = client.get("/recordings?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_missing_recording_404():
    assert client.get("/recordings/9999999").status_code == 404


def test_label_distribution():
    response = client.get("/stats/labels")
    assert response.status_code == 200
