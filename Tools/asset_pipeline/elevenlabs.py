"""
ASHFALL — ElevenLabs voiceover generation.

Synthesises the slice's narration lines to mp3 in Tools/Incoming/audio/vo/.
These are original generated performances (recorded in the manifest).

    python3 -m Tools.asset_pipeline.elevenlabs
"""
from __future__ import annotations

import json
import subprocess
import sys

from ._common import ENV, source_dir, write_manifest

API = "https://api.elevenlabs.io/v1"

# label -> narration line
LINES = {
    "intro_chronomason": (
        "Pompeii. The day the mountain woke. I have walked into its final hours "
        "to change what cannot be changed. Step between the city's golden noon and "
        "its burning dusk, and you may yet lead its people out of the ash."
    ),
    "guide_lucilla": (
        "Traveler! I see you in both times at once. The stair is buried in the hour "
        "of fire. But in the bright hour, the cart still stands. Move it, and we live."
    ),
    "objective_first": "Find a way to clear the escape before the ash takes the courtyard.",
}


def _key():
    return ENV.get("ELEVENLABS_API_KEY", "")


def list_voices():
    out = subprocess.run(
        ["curl", "-sS", "-m", "30", f"{API}/voices", "-H", f"xi-api-key: {_key()}"],
        capture_output=True, text=True).stdout
    try:
        return json.loads(out).get("voices", [])
    except Exception:
        return []


def pick_voice(voices):
    # Prefer a deep narrator-ish male voice; fall back to the first available.
    for want in ("Adam", "Antoni", "Arnold", "Daniel", "George", "Clyde"):
        for v in voices:
            if want.lower() in (v.get("name", "").lower()):
                return v
    return voices[0] if voices else None


def tts(voice_id, text, dest):
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    cmd = [
        "curl", "-sS", "-m", "120", "-X", "POST",
        f"{API}/text-to-speech/{voice_id}",
        "-H", f"xi-api-key: {_key()}",
        "-H", "Content-Type: application/json",
        "-H", "Accept: audio/mpeg",
        "--data", json.dumps(payload),
        "-o", str(dest), "-w", "%{http_code}",
    ]
    code = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    ok = code == "200" and dest.exists() and dest.stat().st_size > 1000
    if not ok and dest.exists():
        # error came back as JSON in the file
        try:
            print("   error:", dest.read_text()[:200])
        except Exception:
            pass
        dest.unlink(missing_ok=True)
    return ok


def main(argv=None):
    if not _key():
        print("[elevenlabs] no ELEVENLABS_API_KEY — skipping")
        return 0
    voices = list_voices()
    voice = pick_voice(voices)
    if not voice:
        print("[elevenlabs] no voices available")
        return 1
    vid = voice["voice_id"]
    print(f"[elevenlabs] voice: {voice.get('name')} ({vid})")
    out = source_dir("audio") / "vo"
    out.mkdir(parents=True, exist_ok=True)  # curl -o won't create parent dirs
    entries = []
    for label, text in LINES.items():
        dest = out / f"VO_{label}.mp3"
        if tts(vid, text, dest):
            print(f"[elevenlabs]   {label} -> {dest.name}")
            entries.append({"id": f"vo_{label}", "label": label, "type": "vo",
                            "license": "Generated (ElevenLabs)", "voice": voice.get("name"),
                            "text": text, "file": str(dest.relative_to(source_dir("audio")))})
        else:
            print(f"[elevenlabs]   FAIL {label}")
    if entries:
        write_manifest("audio", entries)
    print(f"[elevenlabs] DONE — {len(entries)} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
