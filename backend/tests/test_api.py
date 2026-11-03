from fastapi.testclient import TestClient

from app.domain.catalog import CATALOG
from app.main import app


def test_catalog_and_assets():
    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200
        assert len(client.get("/api/catalog").json()) == 46
        for a in CATALOG:
            response = client.get(a["url"])
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("image/svg+xml")
        assert client.get("/media/not-an-asset.svg").status_code == 404


def test_composition_preserves_catalog_and_common_scale():
    with TestClient(app) as client:
        for detail in ["S", "L"]:
            for format in ["horizontal", "square", "vertical"]:
                data = {
                    "query": "книга, телефон, пазлы, монета, лампа",
                    "mode": "objects",
                    "detail": detail,
                    "format": format,
                    "seed": 12,
                }
                a = client.post("/api/compose", json=data)
                assert a.status_code == 200
                assert len(a.json()["items"]) == 5
                assert 0 < a.json()["commonScale"]
                assert a.json() == client.post("/api/compose", json=data).json()
                assert all(
                    i["object"] in ["book", "phone", "puzzle", "coin", "lamp"]
                    for i in a.json()["items"]
                )


def test_invalid_requests_and_palette():
    with TestClient(app) as client:
        assert (
            client.post(
                "/api/compose", json={"query": "неизвестный предмет", "mode": "objects"}
            ).status_code
            == 422
        )
        assert client.post("/api/compose", json={"query": " "}).status_code == 422
        assert client.post("/api/palette", json={"scheme": "custom"}).status_code == 422
        assert client.post("/api/palette", json={"scheme": "peach"}).status_code == 200


def test_background_roles_are_optional_and_behind_main_objects():
    with TestClient(app) as client:
        payload = {"query": "книга, телефон", "mode": "objects"}
        result = client.post("/api/compose", json=payload).json()
        assert [item["role"] for item in result["items"]] == ["background", "main", "main"]
        result = client.post("/api/compose", json={**payload, "background_objects": False}).json()
        assert all(item["role"] == "main" for item in result["items"])
