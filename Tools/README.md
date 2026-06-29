# ASHFALL — Tooling

Automation that lives **outside** `Content/`. Two layers:

| Folder | Runs under | Purpose |
|---|---|---|
| `asset_pipeline/` | host **Python 3** (`python3`) | Fetch CC0/licensed assets & generate custom assets via the `.env` APIs. Writes raw files to `Tools/Incoming/` (gitignored). |
| `ue/` | Unreal's **embedded Python** (headless commandlet) | Import staged assets, build master materials, assemble levels, set up lighting/FX/audio inside the project. |

## Credentials
All keys come from the project-root `.env` (gitignored). Check what's loaded:
```bash
python3 Tools/env.py            # masked report of detected credentials
```

## Running host fetchers (M2)
```bash
python3 -m Tools.asset_pipeline.polyhaven --type hdris --query "sunset"   # example
```

## Running Unreal Python (headless)
```bash
UE=/Users/Shared/Epic\ Games/UE_5.8
PROJ="/Users/jalenedusei/Documents/Unreal Projects/game/game.uproject"
"$UE/Engine/Binaries/Mac/UnrealEditor-Cmd" "$PROJ" \
  -run=pythonscript -script="$(pwd)/Tools/ue/import_assets.py" \
  -unattended -nosplash -stdout -nopause
```
> Add `-nullrhi` for CPU-only tasks; **omit** it for Nanite builds / `HighResShot`.

## License discipline
Only **CC0**, **CC-BY** (attributed in `docs/ASSET_LICENSES.md`), or **self-generated**
assets are imported into `Content/`. The `Incoming/` staging area is the QA gate
before anything is committed.
