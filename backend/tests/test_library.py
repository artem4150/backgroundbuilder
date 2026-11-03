"""Library invariants: original geometry, palette roles, complete variants."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from app.core.config import ASSETS, ROOT
from app.domain.catalog import CATALOG, PALETTES


def colors(root):
    return {
        v
        for e in root.iter()
        for k, v in e.attrib.items()
        if k in ("fill", "stroke", "stop-color") and v != "none"
    }


def test_complete_library_and_role_independent_size():
    components = [a for a in CATALOG if a["kind"] == "component"]
    assert len(components) == 40
    for obj in {a["object"] for a in components}:
        variants = [a for a in components if a["object"] == obj]
        assert {(a["detail"], a["role"]) for a in variants} == {
            ("S", "main"),
            ("S", "background"),
            ("L", "main"),
            ("L", "background"),
        }
        for detail in ["S", "L"]:
            pair = [a for a in variants if a["detail"] == detail]
            assert len({(a["sceneWidth"], a["sceneHeight"]) for a in pair}) == 1


def test_original_geometry_and_all_palette_variants():
    for a in CATALOG:
        original = ET.parse(ROOT / "Тестовое _ иллюстрации" / a["file"]).getroot()
        base = ASSETS / Path(a["url"]).name
        candidates = (
            [(base, None)]
            if a["kind"] == "background"
            else [(base, PALETTES[0])]
            + [(base.with_name(base.stem + "-" + p["id"] + ".svg"), p) for p in PALETTES[1:]]
        )
        for path, palette in candidates:
            root = ET.parse(path).getroot()

            # Every node, path, transform and non-color attribute is unchanged.
            def geometry(r):
                return [
                    (
                        e.tag,
                        {
                            k: v
                            for k, v in e.attrib.items()
                            if k not in ("fill", "stroke", "stop-color")
                        },
                    )
                    for e in r.iter()
                ]

            assert geometry(root) == geometry(original), path.name
            if palette is None:
                palette = next(p for p in PALETTES if p["id"] == a["scheme"])
            permitted = set(palette["backgroundColors"] + palette["neutralColors"])
            if a.get("role") == "main":
                permitted.update(palette["objectColors"])
            assert colors(root) <= permitted, (path.name, colors(root) - permitted)
            assert not any(
                e.tag.endswith(("image", "script", "foreignObject")) for e in root.iter()
            )
            ids = [e.get("id") for e in root.iter() if e.get("id")]
            assert len(ids) == len(set(ids))
            for e in root.iter():
                for v in e.attrib.values():
                    for ref in re.findall(r"url\(#([^)]*)\)", v):
                        assert ref in ids
