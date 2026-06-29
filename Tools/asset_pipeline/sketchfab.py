"""
ASHFALL — Sketchfab fetcher (license-clean Roman props).

Searches downloadable models filtered to CC0 / CC-BY only, downloads + extracts
the glTF, and records license + author for attribution. CC-BY requires the
recorded attribution to ship in docs/ASSET_LICENSES.md.

    python3 -m Tools.asset_pipeline.sketchfab --dry-run
    python3 -m Tools.asset_pipeline.sketchfab

License discipline: only `cc0` and `by` (CC-BY) slugs are accepted. Anything
else is skipped.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

from ._common import ENV, download, get_json, source_dir, write_manifest

API = "https://api.sketchfab.com/v3"
ACCEPT_LICENSES = {"cc0", "by"}  # CC0, CC-BY (attribution recorded)

# label -> search query for the Pompeii prop set
PROP_REQUESTS = {
    "column":        "roman corinthian column",
    "amphora":       "amphora vase",
    "statue":        "roman statue marble",
    "capital":       "column capital corinthian",
    "fountain":      "roman fountain",
    "vessel":        "clay pot terracotta",
}


def _auth():
    tok = ENV.get("SKETCHFAB_API_KEY", "")
    return {"Authorization": f"Token {tok}"} if tok else {}


def search(query, license_slug, limit=12):
    url = (f"{API}/search?type=models&downloadable=true"
           f"&license={license_slug}&count={limit}&q={query.replace(' ', '%20')}")
    try:
        data = get_json(url)
    except Exception as e:
        print(f"[sketchfab] search FAIL ({query}/{license_slug}): {e}")
        return []
    return data.get("results", [])


def best_model(query):
    """Prefer CC0; fall back to CC-BY. Pick the most-liked usable result."""
    for slug in ("cc0", "by"):
        results = [r for r in search(query, slug)
                   if (r.get("license") or {}).get("slug", slug) in ACCEPT_LICENSES
                   and r.get("isDownloadable", True)]
        if results:
            results.sort(key=lambda r: r.get("likeCount", 0), reverse=True)
            r = results[0]
            r["_license_slug"] = slug
            return r
    return None


def download_model(uid, dest_dir: Path) -> Path | None:
    info = get_json(f"{API}/models/{uid}/download", headers=_auth())
    gltf = (info.get("gltf") or {}).get("url")
    if not gltf:
        print(f"[sketchfab] no glTF download url for {uid}")
        return None
    zip_path = dest_dir / "model.zip"
    download(gltf, zip_path)
    try:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(dest_dir)
    except zipfile.BadZipFile:
        print(f"[sketchfab] bad zip for {uid}")
        return None
    zip_path.unlink(missing_ok=True)
    scenes = list(dest_dir.rglob("*.gltf")) + list(dest_dir.rglob("*.glb"))
    return scenes[0] if scenes else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", nargs="*", help="subset of labels to fetch")
    args = ap.parse_args(argv)

    if not ENV.get("SKETCHFAB_API_KEY"):
        print("[sketchfab] no SKETCHFAB_API_KEY in .env — skipping")
        return 0

    entries = []
    for label, query in PROP_REQUESTS.items():
        if args.only and label not in args.only:
            continue
        model = best_model(query)
        if not model:
            print(f"[sketchfab] {label:9} -> no CC0/CC-BY downloadable match")
            continue
        lic = model["_license_slug"]
        author = (model.get("user") or {}).get("displayName", "?")
        print(f"[sketchfab] {label:9} -> {model['name'][:38]!r}  uid={model['uid']} "
              f"license={lic} by {author}")
        if args.dry_run:
            entries.append({"id": model["uid"], "label": label})
            continue
        dest = source_dir("sketchfab") / label
        scene = download_model(model["uid"], dest)
        if scene:
            print(f"[sketchfab]   extracted -> {scene.name}")
            entries.append({
                "id": model["uid"], "label": label, "name": model["name"],
                "type": "model", "license": "CC0" if lic == "cc0" else "CC-BY-4.0",
                "author": author, "source": f"https://sketchfab.com/3d-models/{model['uid']}",
                "scene": str(scene.relative_to(source_dir("sketchfab"))),
            })
    if not args.dry_run and entries:
        write_manifest("sketchfab", entries)
    print(f"[sketchfab] DONE — {len(entries)} models")
    return 0


if __name__ == "__main__":
    sys.exit(main())
