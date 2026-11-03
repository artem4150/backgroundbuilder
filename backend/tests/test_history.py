from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import create_app


class MemoryHistory:
    def __init__(self):
        self.rows = {}

    def list(self, owner):
        return self.rows.get(owner, [])

    def save(self, owner, identifier, snapshot):
        row = {
            "id": identifier,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "snapshot": snapshot,
        }
        self.rows.setdefault(owner, []).insert(0, row)
        return row

    def delete(self, owner, identifier):
        rows = self.rows.get(owner, [])
        self.rows[owner] = [row for row in rows if row["id"] != identifier]
        return len(rows) != len(self.rows[owner])


def snapshot():
    return {
        "query": "книга",
        "mode": "objects",
        "format": "square",
        "detail": "L",
        "scheme": "purple",
        "backgroundObjects": False,
        "commonScale": 1,
        "items": [{"id": 1, "object": "book", "x": 20, "y": 30, "rotation": 0, "role": "main"}],
    }


def test_history_isolated_by_anonymous_cookie():
    app = create_app()
    with TestClient(app) as first, TestClient(app) as second:
        app.state.history = MemoryHistory()
        assert first.get("/api/history").json() == []
        assert first.cookies.get("composition_session")
        response = first.post("/api/history", json=snapshot())
        assert response.status_code == 200
        assert first.get("/api/history").json()[0]["snapshot"] == snapshot()
        assert second.get("/api/history").json() == []


def test_history_rejects_invalid_scene_and_cross_origin():
    app = create_app()
    with TestClient(app) as client:
        app.state.history = MemoryHistory()
        assert (
            client.post("/api/history", json={**snapshot(), "scheme": "unknown"}).status_code == 422
        )
        bad = snapshot()
        bad["items"][0]["object"] = "airplane"
        assert client.post("/api/history", json=bad).status_code == 422
        assert (
            client.get("/api/history", headers={"origin": "https://other.example"}).status_code
            == 403
        )


def test_history_delete_only_own_entry():
    app = create_app()
    with TestClient(app) as first, TestClient(app) as second:
        app.state.history = MemoryHistory()
        row = first.post("/api/history", json=snapshot()).json()
        identifier = row["id"]
        assert second.delete("/api/history/" + identifier).status_code == 404
        assert len(first.get("/api/history").json()) == 1
        assert first.delete("/api/history/" + identifier).status_code == 200
        assert first.get("/api/history").json() == []
