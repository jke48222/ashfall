#!/usr/bin/env python3
"""
ASHFALL — credential loader.

Parses the project-root `.env` (colon-delimited `key: value` format) and exposes
the credentials under canonical, code-friendly names. Secret VALUES are never
printed by this module.

The `.env` file is gitignored and must never be committed. See `.env.example`
for the expected key list.

    from Tools.env import ENV          # if Tools is on sys.path
    # or:  import env; ENV = env.ENV   # when run from inside Tools/

    ENV["SKETCHFAB_API_KEY"]
    ENV.require("ELEVENLABS_API_KEY")  # raises with a helpful message if absent

CLI:
    python Tools/env.py --check        # report which keys are present (masked)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Canonical name -> substrings (lowercased) that identify the matching .env line.
_ALIASES: dict[str, list[str]] = {
    "TUNEE_API_KEY":       ["tunee"],
    "ELEVENLABS_API_KEY":  ["elevenlabs", "eleven labs"],
    "HUGGINGFACE_TOKEN":   ["hugging face", "huggingface"],
    "MODELSLAB_API_KEY":   ["modelslab", "models lab"],
    "EPIC_LOGIN":          ["epic games login", "epic login"],
    "ADOBE_LOGIN":         ["adobe login"],
    "SKETCHFAB_API_KEY":   ["sketchfab"],
    "MESHY_API_KEY":       ["meshy"],
    "FREESOUND_CLIENT_ID": ["freesound client id"],
    "FREESOUND_API_KEY":   ["freesound api key", "freesound client secret", "client secret"],
}

# Sources that require no credential (documented, not flagged as missing).
NO_KEY_REQUIRED = {"POLYHAVEN": "https://api.polyhaven.com"}


def find_project_root(start: Path | None = None) -> Path:
    p = (start or Path(__file__).resolve()).resolve()
    for cand in [p, *p.parents]:
        if (cand / "game.uproject").exists() or (cand / ".env").exists():
            return cand
    return Path(__file__).resolve().parents[1]


def _parse_env_file(path: Path) -> dict[str, str]:
    raw: dict[str, str] = {}
    if not path.exists():
        return raw
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Split on the first ':' or '=' so URLs/colons inside values survive.
        sep = next((s for s in (":", "=") if s in line), None)
        if sep is None:
            continue
        key, val = line.split(sep, 1)
        raw[key.strip().lower()] = val.strip()
    return raw


def _canonicalize(raw: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for canon, needles in _ALIASES.items():
        for rawkey, val in raw.items():
            if val and any(n in rawkey for n in needles):
                out[canon] = val
                break
    # Real process-env overrides / supplements (canonical UPPER_SNAKE keys).
    for k in _ALIASES:
        if os.environ.get(k):
            out[k] = os.environ[k]
    return out


class _Env(dict):
    def require(self, name: str) -> str:
        v = self.get(name)
        if not v:
            raise KeyError(
                f"Missing credential '{name}'. Add it to {ROOT / '.env'} "
                f"(see .env.example)."
            )
        return v


ROOT: Path = find_project_root()
ENV: _Env = _Env(_canonicalize(_parse_env_file(ROOT / ".env")))


def _mask(v: str) -> str:
    if not v:
        return "(empty)"
    if len(v) <= 6:
        return "*" * len(v)
    return f"{v[:3]}…{v[-2:]}  ({len(v)} chars)"


def main(argv: list[str]) -> int:
    print(f"Project root : {ROOT}")
    print(f".env present : {(ROOT / '.env').exists()}")
    print("Credentials (values masked):")
    for canon in _ALIASES:
        present = canon in ENV
        shown = _mask(ENV[canon]) if present else "—  MISSING"
        print(f"  {'OK ' if present else 'MISS'}  {canon:22} {shown}")
    for name, note in NO_KEY_REQUIRED.items():
        print(f"  n/a   {name:22} (no key required — {note})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
