"""
ASHFALL — PolyHaven fetcher (CC0, no account required).

Selects the best-matching textures for a Pompeii material kit from the live
PolyHaven catalog and downloads UE-ready PBR maps (BaseColor / DirectX normal /
ORM-packed `arm` / height), plus two mood HDRIs (Zenith sun, Fall gloom).

    python3 -m Tools.asset_pipeline.polyhaven            # 2k kit (default)
    python3 -m Tools.asset_pipeline.polyhaven --res 4k   # AAA close-up fidelity

Everything here is CC0 1.0 (public domain) — no attribution legally required;
provenance is still recorded in Tools/Incoming/polyhaven/manifest.json.
"""
from __future__ import annotations

import argparse
import sys

from ._common import download, get_json, human_mb, source_dir, write_manifest

API = "https://api.polyhaven.com"

# label -> (must-match keywords, avoid keywords). An asset is only eligible if it
# matches >=1 keyword AND no avoid term; popularity is a tie-break among matches.
MATERIAL_REQUESTS = {
    "marble":       (["marble"], ["mosaic", "tiles"]),
    "plaster_wall": (["plaster", "plastered", "stucco"], ["floor"]),
    "roman_brick":  (["brick"], ["plywood"]),
    "cobblestone":  (["cobblestone", "cobble", "paving", "pavement", "setts"], []),
    "floor_tiles":  (["mosaic", "marble_tiles", "tiled_floor", "tiles"], ["roof"]),
    "roman_concrete": (["concrete"], ["floor", "tiles"]),
    "wood_planks":  (["planks", "wooden_planks", "wood_plank"], ["laminate"]),
    "roof_tiles":   (["roof_tiles", "roofing", "clay_roof", "terracotta", "shingle"], ["wall", "factory", "interior"]),
    "ash_ground":   (["burned_ground", "dirt", "soil", "ash", "gravel", "ground"], ["floor", "tiles"]),
}

# HDRIs: (label, prefer keywords, avoid keywords)
HDRI_REQUESTS = [
    ("zenith_sky", ["sunny", "day", "clear", "afternoon", "noon"], ["night", "indoor", "studio", "moon"]),
    ("fall_sky",   ["overcast", "sunset", "storm", "cloudy", "dramatic", "evening"], ["night", "indoor", "studio"]),
]


def _haystack(asset_id: str, meta: dict) -> str:
    return " ".join([
        asset_id,
        meta.get("name", ""),
        " ".join(meta.get("tags", []) or []),
        " ".join(meta.get("categories", []) or []),
    ]).lower()


def _select(catalog: dict, keywords: list[str], avoid: list[str]):
    """Best asset that matches >=1 keyword and no avoid term; popularity breaks ties."""
    best = None
    best_key = (0, -1)
    for aid, meta in catalog.items():
        hay = _haystack(aid, meta)
        if any(a in hay for a in avoid):
            continue
        matches = sum(1 for kw in keywords if kw in hay)
        if matches == 0:
            continue
        key = (matches, int(meta.get("download_count", 0)))
        if key > best_key:
            best_key, best = key, (aid, meta)
    return best


def _pick_url(files: dict, mapkey: str, res: str, fmts: list[str]):
    block = files.get(mapkey)
    if not block:
        return None
    for r in (res, "2k", "4k", "1k", "8k"):
        if r in block:
            for fmt in fmts:
                if fmt in block[r] and block[r][fmt].get("url"):
                    return block[r][fmt]["url"]
    return None


def fetch_textures(res: str, dry_run: bool = False) -> list[dict]:
    print("[polyhaven] querying texture catalog ...")
    catalog = get_json(f"{API}/assets?type=textures")
    print(f"[polyhaven] {len(catalog)} textures in catalog")
    out = []
    for label, (keywords, avoid) in MATERIAL_REQUESTS.items():
        pick = _select(catalog, keywords, avoid)
        if not pick:
            print(f"[polyhaven] WARN no match for '{label}' (keywords={keywords})")
            continue
        best_id, best_meta = pick
        print(f"[polyhaven] {label:13} -> {best_id}  ({best_meta.get('name', '')})")
        if dry_run:
            out.append({"id": best_id, "label": label})
            continue

        files = get_json(f"{API}/files/{best_id}")
        dest = source_dir("polyhaven") / "textures" / label
        # Prefer the packed ORM ('arm'); only grab separate rough/ao as a fallback.
        wanted = {
            "diffuse": ("Diffuse", ["jpg", "png"]),
            "normal":  ("nor_dx", ["png", "jpg"]),
            "arm":     ("arm", ["png", "jpg"]),
            "height":  ("Displacement", ["png", "jpg"]),
        }
        if not _pick_url(files, "arm", res, ["png", "jpg"]):
            wanted["rough"] = ("Rough", ["png", "jpg"])
            wanted["ao"] = ("AO", ["png", "jpg"])

        got = {}
        for mtype, (mapkey, fmts) in wanted.items():
            url = _pick_url(files, mapkey, res, fmts)
            if not url:
                continue
            ext = url.split(".")[-1].split("?")[0]
            fp = dest / f"{label}_{mtype}.{ext}"
            try:
                download(url, fp)
                got[mtype] = fp.name
                print(f"[polyhaven]   {label}/{mtype} ({human_mb(fp)} MB)")
            except Exception as e:
                print(f"[polyhaven]   FAIL {label}/{mtype}: {e}")
        if got:
            out.append({
                "id": best_id, "label": label, "name": best_meta.get("name", best_id),
                "type": "texture", "license": "CC0",
                "author": ", ".join((best_meta.get("authors") or {}).keys()),
                "source": f"https://polyhaven.com/a/{best_id}", "res": res, "maps": got,
            })
    return out


def fetch_hdris(res: str, dry_run: bool = False) -> list[dict]:
    print("[polyhaven] querying HDRI catalog ...")
    catalog = get_json(f"{API}/assets?type=hdris")
    out = []
    used = set()
    for label, prefer, avoid in HDRI_REQUESTS:
        def hscore(kv):
            aid, meta = kv
            if aid in used:
                return (-1, -1)
            hay = (aid + " " + meta.get("name", "") + " " + " ".join(meta.get("tags", []) or [])).lower()
            if any(a in hay for a in avoid):
                return (-1, -1)
            return (sum(1 for k in prefer if k in hay), int(meta.get("download_count", 0)))
        best_id, best_meta = max(catalog.items(), key=hscore)
        if hscore((best_id, best_meta))[0] <= 0:
            print(f"[polyhaven] WARN no distinct HDRI match for {label}")
            continue
        used.add(best_id)
        print(f"[polyhaven] HDRI {label:11} -> {best_id}")
        if dry_run:
            out.append({"id": best_id, "label": label})
            continue
        files = get_json(f"{API}/files/{best_id}")
        url = _pick_url(files, "hdri", res, ["hdr", "exr"])
        if not url:
            print(f"[polyhaven] WARN no hdr url for {label}")
            continue
        fp = source_dir("polyhaven") / "hdri" / f"{label}.hdr"
        download(url, fp)
        print(f"[polyhaven]   HDRI {label} ({human_mb(fp)} MB)")
        out.append({
            "id": best_id, "label": label, "name": best_meta.get("name", best_id),
            "type": "hdri", "license": "CC0",
            "author": ", ".join((best_meta.get("authors") or {}).keys()),
            "source": f"https://polyhaven.com/a/{best_id}", "res": res, "file": fp.name,
        })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="2k", choices=["1k", "2k", "4k", "8k"])
    ap.add_argument("--skip-hdri", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print selections without downloading")
    args = ap.parse_args(argv)

    entries = fetch_textures(args.res, dry_run=args.dry_run)
    if not args.skip_hdri:
        entries += fetch_hdris("4k", dry_run=args.dry_run)  # sky backdrop always 4k
    if not args.dry_run:
        p = write_manifest("polyhaven", entries)
        print(f"[polyhaven] DONE — {len(entries)} assets; manifest -> {p}")
    else:
        print(f"[polyhaven] DRY RUN — {len(entries)} selections (nothing downloaded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
