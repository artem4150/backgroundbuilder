"""Deterministic composition of immutable SVG objects using a shared scene scale."""

import math
import random

FORMATS = {"horizontal": (1200, 750), "square": (1000, 1000), "vertical": (750, 1200)}
# Small semantic accents stay colored. Large supporting silhouettes can become background.
BACKGROUND_PRIORITY = {"book": 5, "lamp": 5, "tulips": 5, "folder": 4, "headphones": 3}


def intersection(a, b):
    x, y, w, h = a
    xx, yy, ww, hh = b
    return max(0, min(x + w, xx + ww) - max(x, xx)) * max(0, min(y + h, yy + hh) - max(y, yy))


def build_composition(objects, catalog, detail, format, background_objects, seed):
    objects = list(objects)
    contextual = {
        "wallet": "lamp",
        "coin": "folder",
        "headphones": "tulips",
        "puzzle": "book",
        "phone": "book",
        "pen": "book",
        "book": "lamp",
        "folder": "lamp",
        "lamp": "book",
        "tulips": "book",
    }
    primary = objects[0]
    if background_objects and not any(o in BACKGROUND_PRIORITY for o in objects[1:]):
        partner = contextual.get(primary, "book")
        if partner not in objects:
            objects.append(partner)
    rng = random.Random(seed)
    w, h = FORMATS[format]
    factor = 0.55 if detail == "L" else 1.1
    sizes = {
        obj: (
            next(
                a
                for a in catalog
                if a.get("object") == obj and a.get("detail") == detail and a.get("role") == "main"
            )["sceneWidth"]
            * factor,
            next(
                a
                for a in catalog
                if a.get("object") == obj and a.get("detail") == detail and a.get("role") == "main"
            )["sceneHeight"]
            * factor,
        )
        for obj in objects
    }
    # Input order expresses semantic importance, but a tiny coin/pen cannot anchor a full scene.
    hero = next((obj for obj in objects if obj not in ("coin", "pen")), objects[0])
    support = [o for o in objects if o != hero]
    background = (
        max(
            (o for o in support if o in BACKGROUND_PRIORITY),
            key=lambda o: BACKGROUND_PRIORITY[o],
            default=None,
        )
        if background_objects
        else None
    )
    hw, hh = sizes[hero]
    placed = [{"object": hero, "x": -hw / 2, "y": -hh / 2, "role": "main", "rotation": 0}]
    # Diagonal groups follow the isometric source illustrations, with format-specific directions.
    if format == "vertical":
        anchors = [(0.22, -0.75), (-0.22, 0.75), (0.42, 0.2), (-0.42, -0.2), (0.1, 1.25)]
    elif format == "horizontal":
        anchors = [(0.75, -0.28), (-0.75, 0.28), (0.3, 0.65), (-0.3, -0.65), (1.15, 0.2)]
    else:
        anchors = [(0.62, -0.48), (-0.58, 0.5), (0.5, 0.52), (-0.48, -0.55), (0, 0.95)]
    if seed % 2:
        anchors = [(-x, y) for x, y in anchors]
    # Place large background supports before colored accents so they cannot cover the foreground.
    support = [o for o in support if o != background]
    support.sort(key=lambda obj: -sizes[obj][0] * sizes[obj][1])
    for obj in support:
        ow, oh = sizes[obj]
        role = "background" if obj == background else "main"
        candidates = []
        for ax, ay in anchors:
            for distance in (0.65, 0.85, 1.05):
                cx = ax * (hw + ow) * 0.62 * distance
                cy = ay * (hh + oh) * 0.68 * distance
                x, y = cx - ow / 2, cy - oh / 2
                box = (x, y, ow, oh)
                penalty = 0
                for other in placed:
                    pw, ph = sizes[other["object"]]
                    overlap = intersection(box, (other["x"], other["y"], pw, ph)) / min(
                        ow * oh, pw * ph
                    )
                    limit = 0.42 if role == "background" or other["role"] == "background" else 0.30
                    penalty += max(0, overlap - limit) * 40 + overlap * 0.3
                boxes = [(p["x"], p["y"], *sizes[p["object"]]) for p in placed] + [box]
                bw = max(x + ww for x, y, ww, hh in boxes) - min(x for x, y, ww, hh in boxes)
                bh = max(y + hh for x, y, ww, hh in boxes) - min(y for x, y, ww, hh in boxes)
                penalty += (
                    abs(math.log((bw / bh) / (w / h))) * 0.35
                    + distance * 0.35
                    + rng.random() * 0.025
                )
                candidates.append((penalty, x, y))
        _, x, y = min(candidates)
        placed.append({"object": obj, "x": x, "y": y, "role": role, "rotation": 0})
    left = min(p["x"] for p in placed)
    top = min(p["y"] for p in placed)
    right = max(p["x"] + sizes[p["object"]][0] for p in placed)
    bottom = max(p["y"] + sizes[p["object"]][1] for p in placed)
    scale = min(w * 0.82 / (right - left), h * (0.58 if background else 0.84) / (bottom - top), 1.8)
    if background:
        bgw, bgh = sizes[background]
        scale = min(scale, w * 0.88 / bgw, h * 0.88 / bgh)
    dx = (w - (right - left) * scale) / 2
    dy = (h - (bottom - top) * scale) * (0.72 if background else 0.5)
    for p in placed:
        p["x"] = round((p["x"] - left) * scale + dx, 3)
        p["y"] = round((p["y"] - top) * scale + dy, 3)
    if background:
        bw, bh = sizes[background]
        bw *= scale
        bh *= scale
        # Keep the recognizable upper silhouette inside the frame, not just its base.
        by = h * 0.05
        candidates = [w * 0.06, max(w * 0.06, w * 0.94 - bw)]

        def obscured_head(bx):
            key = (bx + bw * 0.35, by, bw * 0.6, bh * 0.40)
            return sum(
                intersection(
                    key,
                    (p["x"], p["y"], sizes[p["object"]][0] * scale, sizes[p["object"]][1] * scale),
                )
                for p in placed
            )

        bx = min(candidates, key=obscured_head)
        placed.insert(
            0,
            {
                "object": background,
                "x": round(bx, 3),
                "y": round(by, 3),
                "role": "background",
                "rotation": 0,
            },
        )
    # Fit the whole group to the frame, using one multiplier for every object.
    gx = min(p["x"] for p in placed)
    gy = min(p["y"] for p in placed)
    gr = max(p["x"] + sizes[p["object"]][0] * scale for p in placed)
    gb = max(p["y"] + sizes[p["object"]][1] * scale for p in placed)
    fill = min(w * 0.94 / (gr - gx), h * 0.94 / (gb - gy))
    ox = (w - (gr - gx) * fill) / 2
    oy = (h - (gb - gy) * fill) / 2
    for p in placed:
        p["x"] = round((p["x"] - gx) * fill + ox, 3)
        p["y"] = round((p["y"] - gy) * fill + oy, 3)
    scale *= fill
    placed.sort(key=lambda p: p["role"] != "background")
    return {"items": placed, "commonScale": scale, "hero": hero, "layout": "diagonal-cluster"}
