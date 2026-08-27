# Ashfall

A framework for a time-travel puzzle game set in Pompeii on the day Vesuvius erupts. You play a
Chronomason, someone who can flip the same city block between two moments: **Zenith**, the living
city at golden noon, and **Fall**, the eruption itself, with ash in the air, fire in the courtyard,
and columns already down. One button switches between them. You compare the two to work out what
kills people, then change something in Zenith so a different Fall happens.

**Read this first.** This repository is a vertical-slice *framework*, verified headlessly. It has
never been played. There is no playable build, no packaged game, and no screenshots or video. What
exists is a compiled C++ gameplay framework, an automated level build, a 600 MB asset set, and a
suite of assertions that drive and check the gameplay systems from the command line with no game
window open. The [Status](#status) section spells out exactly what that means.

## What problem this solves

The design problem is making time travel legible. A player who flips between two versions of a place
needs to understand, without a tutorial, what a change in one does to the other. The
[game design document](docs/GDD.md) frames the slice as 70 percent environmental puzzle, 20 percent
stealth, and 10 percent action, with the flagship puzzle being "The Blocked Stair of the House of the
Vettii": a family is trapped upstairs in the Fall because rubble buries the stairway, so in Zenith you
reroute the cart that will fall and bury it, and open the cistern valve that will later flood the fire
blocking the courtyard.

The engineering problem is what this repo actually attacks. Two-state worlds are expensive if you
build them naively, and hard to test at all. Duplicating every asset doubles the memory budget and
guarantees the two versions drift apart. And gameplay logic in a game engine is normally only
testable by launching the game and playing it, which means nobody tests it.

Ashfall's answer to the first is one shared piece of geometry per object that morphs, driven by a
per-actor config, instead of two copies. Its answer to the second is the design decision described
below, which lets a Python script drive the entire gameplay state machine from a headless process.

## How it works

Three C++ pieces carry the mechanic, all under
[`Source/game/Ashfall/`](Source/game/Ashfall):

**`UTemporalSubsystem`** ([Temporal/TemporalSubsystem.cpp](Source/game/Ashfall/Temporal/TemporalSubsystem.cpp))
is the single authority on which time state is active. It holds the current state, a registry of every
object that cares, and a set of *causal flags*: named booleans recording that the player changed
something. `SetCausalFlag("Vettii.StairCleared", true)` in Zenith is what makes a different Fall
possible.

The registry is a `TArray<TWeakObjectPtr<UTemporalStateComponent>>`, which matters for two reasons.
Weak pointers mean a destroyed actor cannot leave a dangling entry, and `BroadcastState` walks the
array backwards so it can prune dead entries with `RemoveAtSwap` while iterating. And
`RegisterComponent` snaps a newcomer to the current state immediately, so an actor spawned or streamed
in while the world is in Fall is never briefly wrong.

**`UTemporalStateComponent`** ([Temporal/TemporalStateComponent.cpp](Source/game/Ashfall/Temporal/TemporalStateComponent.cpp))
is what you attach to an actor to make it two-state. It stores one `FTemporalStateConfig` per state
(a local transform offset, a visibility flag, a material override, a physics-simulation flag) and
applies the right one on change. Transforms are composed against a base captured at `BeginPlay`, so
offsets are authored in the actor's local frame and a level designer can move the actor without
re-authoring the offsets. The component only ticks while a blend is actually running, and disables
its own tick the moment the blend finishes.

**`UAshfallObjectiveSubsystem`** ([Puzzle/AshfallObjectiveSubsystem.cpp](Source/game/Ashfall/Puzzle/AshfallObjectiveSubsystem.cpp))
tracks the win condition: rescue `CitizensToSave` citizens (default 6, configurable in Project
Settings via `UAshfallSettings`) and the objective flips to `Won`. The saved count clamps at the
total.

### The part worth reading: a UE gameplay system that unit tests itself

One line does most of the work here. In `TemporalSubsystem.cpp`:

```cpp
bool UTemporalSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game
		|| WorldType == EWorldType::PIE
		|| WorldType == EWorldType::Editor
		|| WorldType == EWorldType::EditorPreview;
}
```

`Editor` is the interesting entry. A `UWorldSubsystem` is an engine-managed object scoped to a world;
by default the gameplay ones exist only in the Game and Play-In-Editor worlds, because that is where
gameplay happens. Including `EWorldType::Editor` means the authoritative time-state machine, the causal
flag store, and (via the same override on the objective subsystem) the whole win condition are alive in
the *editor* world.

That is what makes the rest possible. Unreal's embedded Python can fetch the editor world and call into
these subsystems through
[`UAshfallTemporalLibrary`](Source/game/Ashfall/Temporal/AshfallTemporalLibrary.h), a
`UBlueprintFunctionLibrary` that exists so both Blueprints and Python get the same entry points. So the
gameplay systems can be driven and asserted from a command-line process with `-nullrhi` (no rendering
device), `-unattended`, and `-nosplash`. No game window, no human, no frames rendered.

[`Tools/ue/validate_m4.py`](Tools/ue/validate_m4.py) uses that to walk the actual core loop:

```
set state to Zenith
set causal flag "Vettii.StairCleared"        (what an interaction does)
toggle to Fall
  assert the world is in Fall
  assert the causal flag survived the toggle  <-- the whole mechanic, in one assert
rescue citizens one at a time, asserting the count after each
  assert the objective flipped to Won at the target
rescue once more
  assert the saved count clamps at the total
```

Gameplay code in a game engine is usually only testable by launching the game. This one is testable
the way a library is.

**Where the causal flags live matters.** `Deinitialize` calls `CausalFlags.Reset()`, so flags are
in-memory only. They persist across time toggles within a session, which is exactly what the mechanic
requires. They do not persist across sessions. There is no save system in this repo; the
[architecture doc](docs/ARCHITECTURE.md) lists one as planned.

### Interaction

[`UInteractableComponent`](Source/game/Ashfall/Interaction/InteractableComponent.cpp) is the bridge
between the player and the causality system. Attach it to an actor, give it a `CausalFlag` name, and
interacting sets that flag on the subsystem. It supports single-use semantics and broadcasts an
`OnInteracted` delegate. `UTemporalControlComponent` on the player owns the toggle verb and enforces a
cooldown (default 0.5 s) so the world cannot be strobed.

## Results

Everything below is a count taken from this repository. There is no performance data of any kind: no
frame rate, no Unreal Insights trace, no packaged build to measure. The
[architecture doc](docs/ARCHITECTURE.md) states a 60 fps target at 1440p, which is a stated budget and
has never been measured.

| Fact | Value | Notes |
| --- | --- | --- |
| Engine | Unreal Engine 5.8 | `game.uproject` `EngineAssociation: "5.8"`, installed at `/Users/Shared/Epic Games/UE_5.8` |
| Original C++ | 1,333 lines across 26 files | `Source/game/Ashfall/` only, excluding the stock template in `Source/game/Variant_*` |
| Headless assertions | 32 checks at run time | 24 `expect(...)` call sites in the two validators; two of them sit inside loops (4 type registrations, 6 citizen rescues) and expand |
| Compile-verified milestones | 2 of 7 | M1 and M4 record "Build: gameEditor Mac Development, Succeeded" |
| Headless-validated level builds | 2 | M3 and M5 record actor counts from level generation (35 temporal, 11 static, 5 light, 0 failures), which is a level build, not a C++ compile |
| PBR material sets | 9 | marble, cobblestone, roman_concrete, ash_ground, plaster_wall, floor_tiles, roof_tiles, roman_brick, wood_planks, each with base color, normal, ORM, and height |
| Photoscan props | 6 prop sets, 87 static mesh assets | amphora 7, capital 12, column 25, fountain 29, statue 8, vessel 6. Each downloaded set decomposed into many meshes on glTF import, so 87 is an asset count, not 87 distinct props |
| Audio | 6 sound effects, 3 voice-over lines | `Content/Ashfall/Audio/` |
| Level | `Content/Ashfall/Maps/L_Pompeii_VS.umap` | Generated by the 420-line [`Tools/ue/build_level.py`](Tools/ue/build_level.py). `Content/Ashfall/` totals 600 MB, tracked with Git LFS |
| Browser demo | 490 lines across 6 JavaScript files | `web/src/`, see below |

**Nanite is explicitly enabled per mesh** in
[`Tools/ue/import_models.py:32`](Tools/ue/import_models.py) (Nanite is Unreal's virtualized geometry
system, which streams and renders very dense meshes without hand-authored levels of detail, and dense
photoscans are exactly what it is for). But `enable_nanite` has a fallback path that logs
`nanite FAIL` and returns false, and the import result was not committed, so it is not provable that
all 87 meshes ended up with Nanite on. Lumen and Virtual Shadow Maps are on, but they are Unreal 5
defaults rather than anything configured in this repo, so they are not listed as achievements here.

**Where the architecture doc runs ahead of the code.** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
describes `UTemporalCausalityComponent`, `ATemporalPuzzleManager`, `UPuzzleNodeComponent`, a
`Save/` module, and Data Layer driven set dressing. None of those exist in `Source/`. Causality is
currently the flat causal-flag set on the subsystem, and the objective is the citizen counter. Read
that document as the intended architecture, not an inventory.

## Running it

Requirements: macOS, Unreal Engine 5.8 at `/Users/Shared/Epic Games/UE_5.8`, Git with
[Git LFS](https://git-lfs.com), and Python 3.

```bash
git lfs install
git clone <this-repo> && cd ashfall
cp .env.example .env      # asset-pipeline API keys, gitignored
python3 Tools/env.py      # verify credentials load (values are masked in the output)
```

Build the editor target with the editor closed. New `UCLASS`es need a full rebuild on macOS, where
Live Coding is limited, which is why C++ changes in this repo are batched one commit per milestone.

```bash
"/Users/Shared/Epic Games/UE_5.8/Engine/Build/BatchFiles/Mac/Build.sh" \
  game Mac Development -project="$(pwd)/game.uproject"
```

A successful build prints `Build: gameEditor Mac Development, Succeeded` (this is the line quoted in
the M1 and M4 commit messages). Then open `game.uproject` in the editor, or run the headless
validators, which is the path this repo is actually built around:

```bash
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor-Cmd"

ASHFALL_M1_RESULT=/tmp/m1.txt "$UE" "$(pwd)/game.uproject" -run=pythonscript \
  -script="$(pwd)/Tools/ue/validate_m1.py" -unattended -nosplash -nullrhi -stdout -nopause

ASHFALL_M4_RESULT=/tmp/m4.txt "$UE" "$(pwd)/game.uproject" -run=pythonscript \
  -script="$(pwd)/Tools/ue/validate_m4.py" -unattended -nosplash -nullrhi -stdout -nopause
```

Each writes a result file whose last line is the verdict. A successful run ends with
`[M1] RESULT: ALL PASS` or `[M4] RESULT: ALL PASS`. The scripts write to a file rather than relying
on stdout because Unreal only surfaces `unreal.log*` output, not Python `print()`.

Other scripts in [`Tools/ue/`](Tools/ue) run the same way:
`build_level.py` regenerates the level from scratch, `import_kit.py` and `import_models.py` import
staged assets, `import_audio.py` imports audio. They all read from `Tools/Incoming/`, which is
gitignored, so they only work after the fetchers in
[`Tools/asset_pipeline/`](Tools/asset_pipeline) have run with valid API keys.

### Running the browser demo

The `web/` directory is independent of the Unreal project and needs only Node.

```bash
cd web
npm install
npm run dev
```

Then open the printed URL and press **Q** (or T, or Space, or the on-screen button) to shift time.
The next section describes exactly what it is and is not.

## What the browser demo actually is

`web/` is **a camera diorama, not a game.** You orbit a mouse around a Roman courtyard and press one
key to blend it between Zenith and Fall. Materials and visibility swap instantly, and the mood eases
over roughly a second and a half: the sun goes from warm white at intensity 3.2 to ember orange at
1.25, fog closes from 90 to 16 units, tone-mapping exposure drops, the sky background swaps for a
burnt HDRI, 6,000 ash particles fade in ([`web/src/fx.js:5`](web/src/fx.js)), cobblestone becomes
burned ground, plaster becomes scorched brick, standing columns hide while pre-placed fallen twins
appear, the fountain's water surface vanishes, rubble piles appear, and two ambient audio beds
(market crowd, fountain) crossfade into three (fire, ash wind, tremor) under a transition stinger.

What it does **not** have: a player character, walking, collision, interaction, an objective, or a win
condition. [`web/src/world.js:11`](web/src/world.js) reads, verbatim:

```js
const interactables = []; // filled in W4
```

It was never filled. The array is returned and never used.

The demo is built entirely from three.js primitives (boxes, cylinders, planes) textured with the same
PBR maps as the Unreal kit. It uses **zero** of the 87 Unreal mesh assets. It is a fast, honest
illustration of the time-toggle idea in a browser, and nothing more.

## Asset pipeline and licensing

Two halves. Host Python in [`Tools/asset_pipeline/`](Tools/asset_pipeline) fetches assets into
`Tools/Incoming/`, and Unreal Python in [`Tools/ue/`](Tools/ue) imports them into `Content/`.

The sources are not all the same kind of thing, and the distinction matters:

- **PolyHaven** (`polyhaven.py`) pulls CC0 textures and HDRIs. No attribution legally required.
- **Sketchfab** (`sketchfab.py`) pulls CC0 and CC-BY photoscan models. The CC-BY ones (column,
  amphora, capital, fountain, vessel) **require** attribution and must ship with the game.
- **Freesound** (`freesound.py`) pulls CC0 sound effects.
- **ElevenLabs** (`elevenlabs.py`) does not pull anything. It **generates** voice-over. The three VO
  assets in `Content/Ashfall/Audio/VO/` are AI-synthesized original narration, not licensed
  recordings. [`docs/ASSET_LICENSES.md`](docs/ASSET_LICENSES.md) puts them under their own
  "Self-generated (AI) assets" heading rather than burying them among the CC0 tables.

Each fetcher writes a machine-readable `manifest.json` recording author, URL, license, and date. Those
manifests go to `Tools/Incoming/`, which is gitignored, so they are not the durable record.
[`docs/ASSET_LICENSES.md`](docs/ASSET_LICENSES.md) is: a human-readable attribution ledger,
reconciled from the manifests and committed, listing every asset with its source and license.

## Project layout

```
Source/game/
├── Ashfall/                 All original C++ (1,333 lines, 26 files)
│   ├── Temporal/                TemporalSubsystem (the authority), TemporalStateComponent
│   │                            (per-actor two-state config), TemporalProp, TemporalTypes.h,
│   │                            TemporalLightingDirector, AshfallTemporalLibrary
│   │                            (the Blueprint and Python entry points)
│   ├── Puzzle/                  AshfallObjectiveSubsystem (the win condition)
│   ├── Interaction/             InteractableComponent, IInteractable
│   ├── Player/                  AshfallCharacter (disabled, see Status),
│   │                            AshfallPlayerController, TemporalControlComponent
│   ├── Core/                    AshfallGameMode
│   └── Config/                  AshfallSettings (UDeveloperSettings)
└── Variant_*/               Stock Unreal template code, unmodified. The Combat variant is
                             the intended base for the action fail-state

Content/Ashfall/             600 MB, Git LFS
├── Maps/L_Pompeii_VS.umap       The vertical-slice level, script-generated
├── Kit/Textures/                9 PBR sets
├── Kit/Props/                   6 photoscan sets, 87 static mesh assets
├── Kit/HDRI/                    Zenith and Fall skies
└── Audio/                       6 SFX, 3 VO

Tools/
├── asset_pipeline/          Host Python: fetch and generate into gitignored Tools/Incoming/
└── ue/                      Unreal Python: import, build the level, and validate headlessly

web/                         The three.js browser demo (490 lines). Independent of the UE project
docs/                        GDD, architecture, asset licenses, roadmap
```

## Status

**Compiled and headless-verified. Never played.**

What is true:

- Two commits (M1, M4) record `Build: gameEditor Mac Development, Succeeded`, so the C++ compiled at
  those points.
- Both validators report `ALL PASS`, so 32 assertions passed against the real subsystems in a real
  editor world.
- The level exists as a committed 600 MB asset set, generated by a script that reports its own actor
  counts.

What is not true, and is worth stating plainly because a reader will otherwise assume it:

- **There is no playable build.** No `Binaries/`, `Intermediate/`, `Saved/`, or `DerivedDataCache/`
  directory exists at this path. The absence of `Saved/` is the giveaway: Unreal creates it the first
  time the editor opens a project. This project has never been opened in the editor here, and
  Play-In-Editor has never been entered.
- **There are no screenshots or video.** `AshfallGameMode::BeginPlay` has an opt-in `-AshfallAutoShot`
  hook ([Core/AshfallGameMode.cpp:36](Source/game/Ashfall/Core/AshfallGameMode.cpp)) that waits six
  seconds for shaders, captures Zenith at 1920x1080, toggles to Fall, captures again, and quits. It is
  a headless capture path and no output from it was ever committed.
- **The custom player character is disabled because it crashes.** `AAshfallCharacter` inherits from
  the template's `ACombatCharacter`, which asserts on a missing LifeBar widget that only a Blueprint
  can supply. `AAshfallGameMode`'s constructor therefore sets `DefaultPawnClass` to the stock
  `BP_ThirdPersonCharacter` and falls back to `AAshfallCharacter` only if that Blueprint is missing.
  See commit `a3f3ce5`. The temporal toggle is pawn-agnostic (it lives on the world subsystem), so
  this does not block the mechanic, but the character with the temporal control component attached is
  not the one that would spawn.
- **No performance data exists.** No trace, no frame timing, no packaged build.
- **The Unreal project and the browser demo share no code and no assets.** They are two independent
  expressions of the same idea in one repository.

Next steps, in the order they unblock the most:

1. Open the project in the editor once and enter Play-In-Editor. Everything below depends on knowing
   whether the level actually loads and looks like the intent.
2. Author the LifeBar Blueprint so `AAshfallCharacter` can spawn, which is what puts the temporal
   control component on the pawn the player controls.
3. Run `-AshfallAutoShot` and commit the two captures. A Zenith and Fall pair of the same camera angle
   is the single most persuasive artifact this project could have.
4. Build the Blocked Stair puzzle from the GDD as real actors. The framework supports it (causal flag,
   interactable, objective), but the level does not contain it.
5. Replace the flat causal-flag set with the data-driven causality component the architecture doc
   describes, so puzzles become content rather than code.

## License and credits

Code: see [`LICENSE`](LICENSE). Every third-party asset is CC0, CC-BY with attribution, Epic template
content under the Unreal Engine EULA, or AI-generated for this project, all recorded in
[`docs/ASSET_LICENSES.md`](docs/ASSET_LICENSES.md) and [`CREDITS.md`](CREDITS.md).

Two external plugins are referenced but not vendored: Quixel Bridge / FAB (ships with the engine) and
VibeUE, an editor tooling plugin that is Win64-only and therefore non-functional on macOS and not on
the build path.
