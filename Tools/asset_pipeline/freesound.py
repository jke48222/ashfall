"""
ASHFALL — Freesound SFX fetcher (CC0 only).

Searches Freesound filtered to CC0, downloads the HQ-mp3 preview for each cue
into Tools/Incoming/audio/sfx/. CC0 needs no attribution; provenance recorded.

    python3 -m Tools.asset_pipeline.freesound

Token auth uses the Freesound API key (the client-secret value). Full-quality
originals would require OAuth2; HQ previews are sufficient for the slice.
"""
from __future__ import annotations

import json
import subprocess
import sys

from ._common import ENV, download, source_dir, write_manifest

API = "https://freesound.org/apiv2"

# label -> search query (ambient/cue beds for both states)
SFX_REQUESTS = {
    "amb_crowd_market": "market crowd ambience people",
    "amb_water_fountain": "fountain water trickle",
    "fall_fire_crackle": "fire crackling large",
    "fall_rumble_quake": "earthquake low rumble",
    "fall_ash_wind": "wind eerie low drone",
    "stinger_whoosh": "time whoosh transition",
}


def _token():
    # Freesound token auth uses the API key (client secret); fall back to client id.
    return ENV.get("FREESOUND_API_KEY") or ENV.get("FREESOUND_CLIENT_ID") or ""


def search_cc0(query, token):
    url = (f"{API}/search/text/?query={query.replace(' ', '%20')}"
           f"&filter=license:%22Creative%20Commons%200%22"
           f"&fields=id,name,license,username,previews,duration"
           f"&page_size=5&sort=score&token={token}")
    out = subprocess.run(["curl", "-sS", "-m", "30", url], capture_output=True, text=True).stdout
    try:
        return json.loads(out).get("results", [])
    except Exception:
        return []


def main(argv=None):
    token = _token()
    if not token:
        print("[freesound] no Freesound credentials — skipping")
        return 0
    out = source_dir("audio") / "sfx"
    entries = []
    for label, query in SFX_REQUESTS.items():
        results = search_cc0(query, token)
        if not results:
            print(f"[freesound] {label:18} -> no CC0 match")
            continue
        # prefer something with reasonable length
        results.sort(key=lambda r: abs((r.get("duration") or 5) - 8))
        r = results[0]
        prev = (r.get("previews") or {})
        purl = prev.get("preview-hq-mp3") or prev.get("preview-lq-mp3")
        if not purl:
            print(f"[freesound] {label:18} -> no preview url")
            continue
        dest = out / f"SFX_{label}.mp3"
        try:
            download(purl, dest)
        except Exception as e:
            print(f"[freesound] {label:18} -> download FAIL {e}")
            continue
        print(f"[freesound] {label:18} -> {r['name'][:34]!r} by {r.get('username')}")
        entries.append({"id": f"fs_{r['id']}", "label": label, "type": "sfx",
                        "license": "CC0", "author": r.get("username"),
                        "source": f"https://freesound.org/s/{r['id']}/",
                        "file": str(dest.relative_to(source_dir('audio')))})
    if entries:
        write_manifest("audio", entries)
    print(f"[freesound] DONE — {len(entries)} sfx")
    return 0


if __name__ == "__main__":
    sys.exit(main())
