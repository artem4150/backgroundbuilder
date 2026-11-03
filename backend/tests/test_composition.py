import itertools

from app.domain.catalog import CATALOG
from app.domain.composition import FORMATS, build_composition


def test_compositions_keep_every_object_visible_and_relative_scale():
    objects = [
        "book",
        "phone",
        "puzzle",
        "wallet",
        "coin",
        "lamp",
        "folder",
        "pen",
        "headphones",
        "tulips",
    ]
    cases = list(itertools.combinations(objects, 2)) + [tuple(objects[i : i + 5]) for i in range(6)]
    for detail in ["S", "L"]:
        for fmt, (w, h) in FORMATS.items():
            for case in cases:
                result = build_composition(list(case), CATALOG, detail, fmt, True, 12)
                assert {i["object"] for i in result["items"]} >= set(case)
                assert any(i["role"] == "main" for i in result["items"])
                seen_main = False
                for item in result["items"]:
                    if item["role"] == "main":
                        seen_main = True
                    else:
                        assert not seen_main
                    a = next(
                        a
                        for a in CATALOG
                        if a.get("object") == item["object"]
                        and a.get("detail") == detail
                        and a.get("role") == "main"
                    )
                    factor = (0.55 if detail == "L" else 1.1) * result["commonScale"]
                    sw = a["sceneWidth"] * factor
                    sh = a["sceneHeight"] * factor
                    assert item["x"] >= -0.001 and item["y"] >= -0.001
                    assert item["x"] + sw <= w + 0.001 and item["y"] + sh <= h + 0.001


def test_semantic_hero_and_optional_background():
    r = build_composition(["wallet", "lamp", "coin"], CATALOG, "L", "square", True, 12)
    assert r["hero"] == "wallet"
    assert next(i for i in r["items"] if i["object"] == "lamp")["role"] == "background"
    assert next(i for i in r["items"] if i["object"] == "coin")["role"] == "main"
    r = build_composition(["wallet", "lamp", "coin"], CATALOG, "L", "square", False, 12)
    assert all(i["role"] == "main" for i in r["items"])


def test_wallet_coin_have_contextual_background():
    r = build_composition(["wallet", "coin"], CATALOG, "L", "vertical", True, 12)
    assert {(i["object"], i["role"]) for i in r["items"]} == {
        ("wallet", "main"),
        ("coin", "main"),
        ("lamp", "background"),
    }
    r = build_composition(["wallet", "coin"], CATALOG, "L", "vertical", False, 12)
    assert len(r["items"]) == 2


def test_background_lamp_is_fully_inside_each_format():
    for fmt, (w, h) in FORMATS.items():
        r = build_composition(["book", "folder", "pen", "lamp"], CATALOG, "L", fmt, True, 12)
        lamp = next(i for i in r["items"] if i["object"] == "lamp")
        assert lamp["role"] == "background"
        assert lamp["x"] >= 0 and lamp["y"] >= 0
        a = next(
            a
            for a in CATALOG
            if a.get("object") == "lamp" and a.get("detail") == "L" and a.get("role") == "main"
        )
        assert lamp["x"] + a["sceneWidth"] * 0.55 * r["commonScale"] <= w
        assert lamp["y"] + a["sceneHeight"] * 0.55 * r["commonScale"] <= h
