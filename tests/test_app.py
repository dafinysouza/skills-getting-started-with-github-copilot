from pathlib import Path
import sys

# Ensure `src` is on sys.path so we can import `app` directly
sys.path.insert(0, str(Path.cwd() / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister():
    email = "test_student@example.com"
    activity = "Chess Club"

    # Try to remove if already present (be idempotent)
    client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Sign up
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Duplicate signup should return 400
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 400

    # Unregister
    r = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert r.status_code == 200
    assert "Removed" in r.json().get("message", "")


def test_root_redirect():
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers.get("location", "").endswith("/static/index.html")
