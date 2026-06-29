"""
ASHFALL asset-pipeline shared helpers.

HTTP runs through `curl` (the system CA bundle works; Python 3.14's urllib on
this macOS does not), which also gives us redirects + large-file downloads for
free. Every fetcher stages into Tools/Incoming/<source>/ and records provenance
in a per-source manifest.json (reconciled into docs/ASSET_LICENSES.md).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # repo root
INCOMING = ROOT / "Tools" / "Incoming"
sys.path.insert(0, str(ROOT))                          # so `from Tools.env import ENV` works

try:
    from Tools.env import ENV  # noqa: E402
except Exception:               # pragma: no cover - env is optional for CC0 sources
    ENV = {}


def _curl(extra_args, timeout=180):
    return subprocess.run(
        ["curl", "-sS", "-L", "-m", str(timeout), *extra_args],
        capture_output=True, text=True,
    )


def get_json(url, headers=None, timeout=60):
    args = ["-w", "\n%{http_code}", url]
    for k, v in (headers or {}).items():
        args += ["-H", f"{k}: {v}"]
    res = _curl(args, timeout)
    out = res.stdout
    body, _, code = out.rpartition("\n")
    code = code.strip()
    if code != "200":
        raise RuntimeError(f"GET {url} -> HTTP {code or '?'}: {(body or res.stderr)[:300]}")
    return json.loads(body)


def post_json(url, payload, headers=None, timeout=120):
    args = ["-X", "POST", "-w", "\n%{http_code}", url, "--data", json.dumps(payload)]
    hdrs = {"Content-Type": "application/json", **(headers or {})}
    for k, v in hdrs.items():
        args += ["-H", f"{k}: {v}"]
    res = _curl(args, timeout)
    body, _, code = res.stdout.rpartition("\n")
    code = code.strip()
    if code not in ("200", "201", "202"):
        raise RuntimeError(f"POST {url} -> HTTP {code or '?'}: {(body or res.stderr)[:300]}")
    return json.loads(body) if body.strip() else {}


def download(url, dest: Path, headers=None, timeout=900) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    args = ["-o", str(dest), "-w", "%{http_code}", url]
    for k, v in (headers or {}).items():
        args += ["-H", f"{k}: {v}"]
    res = _curl(args, timeout)
    code = res.stdout.strip()
    if code not in ("200", "206") or not dest.exists() or dest.stat().st_size == 0:
        if dest.exists() and dest.stat().st_size == 0:
            dest.unlink(missing_ok=True)
        raise RuntimeError(f"download {url} -> HTTP {code or '?'}")
    return dest


def source_dir(source: str) -> Path:
    d = INCOMING / source
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_manifest(source: str, entries: list[dict]) -> Path:
    """Merge entries (keyed by 'id') into Tools/Incoming/<source>/manifest.json."""
    p = source_dir(source) / "manifest.json"
    by_id: dict = {}
    if p.exists():
        for e in json.loads(p.read_text()):
            by_id[e.get("id")] = e
    for e in entries:
        by_id[e.get("id")] = e
    p.write_text(json.dumps(list(by_id.values()), indent=2))
    return p


def human_mb(path: Path) -> float:
    return round(path.stat().st_size / (1024 * 1024), 2) if path.exists() else 0.0
