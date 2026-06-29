<div align="center">

# ASHFALL — The Last Hours of Pompeii

**A photoreal Unreal Engine 5.8 time-travel game about saving ancient cities from collapse.**

*Toggle the same streets between their golden age and their final hours — and change which one survives.*

</div>

---

## Pitch

You are a **Chronomason**: a traveler who steps into the deep past to avert the
collapse of doomed cities. The flagship chapter is **Pompeii, 79 AD** — hours
before Vesuvius erupts. By flipping each location between its **Zenith** (a living
city) and its **Fall** (the eruption), you diagnose what dooms its people and
intervene in the past so a different future survives.

It is **70% environmental puzzle**, **20% stealth** (navigate crowds and guards),
and **10% action** (a fail-state when the disaster catches you).

## Status

🚧 **Vertical slice in development.** This repository targets one fully-realized,
photoreal city block with the complete core loop, plus a scalable, documented
codebase. It is *not* a finished multi-year title — see [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Tech at a glance

- **Unreal Engine 5.8**, C++ first, built on the Third-Person template.
- **Nanite · Lumen · Virtual Shadow Maps · Volumetric atmosphere** for photoreal fidelity.
- **Two-state temporal system** (`UTemporalSubsystem` + `UTemporalStateComponent`) — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
- Reuses the template's C++ **Combat variant** (AI, StateTree, EQS, damage interfaces) for the action fail-state.
- **Python asset pipeline** pulling CC0 / license-clean assets and generating custom ones.

## Repository layout

```
Source/game/Ashfall/     # New C++ gameplay framework (temporal, puzzle, player, save)
Source/game/Variant_*    # Stock template variants (Combat reused; others reference)
Content/Ashfall/         # Game content (maps, kit, materials, FX, audio, UI)  [Git LFS]
Tools/                   # Python automation (asset_pipeline + ue) — see Tools/README.md
docs/                    # GDD, architecture, asset licenses, roadmap
```

## Getting started

**Requirements:** macOS, Unreal Engine 5.8 (`/Users/Shared/Epic Games/UE_5.8`),
Git + [Git LFS](https://git-lfs.com), Python 3.

```bash
git lfs install
git clone <this-repo> && cd game
# Credentials: copy .env.example -> .env and fill in keys (gitignored)
python3 Tools/env.py            # verify credentials load (values masked)
```

**Build (Mac, editor closed):**
```bash
"/Users/Shared/Epic Games/UE_5.8/Engine/Build/BatchFiles/Mac/Build.sh" \
  game Mac Development -project="$(pwd)/game.uproject"
```

Then open `game.uproject` in the Unreal Editor.

## Required external plugins

These are **not vendored** (installed via FAB / their own distribution):

- **VibeUE** — MCP/AI editor toolset. *Win64-only; non-functional on macOS, not on the build path.*
- **Quixel Bridge / FAB** — asset import (ships with the engine).

## License & credits

Code: see [`LICENSE`](LICENSE) (TBD). Assets: every third-party asset is CC0 or
attributed in [`docs/ASSET_LICENSES.md`](docs/ASSET_LICENSES.md) and [`CREDITS.md`](CREDITS.md).
