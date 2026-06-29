# ASHFALL — Technical Architecture

## 1. Platform reality (macOS)
- Engine: **UE 5.8** at `/Users/Shared/Epic Games/UE_5.8`.
- **Editor automation = Unreal's own Python** (`PythonScriptPlugin`), run headlessly
  via `UnrealEditor-Cmd … -run=pythonscript` and in the live editor.
- **VibeUE is Win64-only** (`WhitelistPlatforms: ["Win64"]`) — its compiled C++
  services do **not** load on macOS and are **not** on the build path. We keep it
  installed only for its markdown skill/reference docs.
- C++ builds: `Engine/Build/BatchFiles/Mac/Build.sh game Mac Development -project=<uproject>`.
  New `UCLASS`es need a full rebuild with the **editor closed** (Mac Live Coding is limited),
  so C++ changes are batched per milestone.

## 2. Module & folder layout
All new gameplay code lives under `Source/game/Ashfall/`, leaving the stock template
variants intact and reusable.

```
Source/game/
├── game.Build.cs            # + Niagara, GeometryCollectionEngine, DeveloperSettings,
│                            #   Json, GameplayTags, MetaSoundEngine (+ existing deps)
├── gameCharacter / gameGameMode / gamePlayerController   # template bases
├── Variant_Combat/          # REUSED: ACombatCharacter, AI(StateTree/EQS), interfaces
└── Ashfall/
    ├── Core/        AshfallGameMode
    ├── Player/      AshfallCharacter (: ACombatCharacter), TemporalControlComponent,
    │                AshfallPlayerController (: AgamePlayerController)
    ├── Temporal/    TemporalTypes.h (ETimeState, FTemporalStateConfig),
    │                TemporalSubsystem (UWorldSubsystem), ITemporalActor,
    │                TemporalStateComponent, TemporalCausalityComponent
    ├── Puzzle/      TemporalPuzzleManager, PuzzleNodeComponent
    ├── Interaction/ InteractableComponent, IInteractable
    ├── Save/        AshfallSaveGame (USaveGame), SaveSubsystem
    └── Config/      AshfallSettings (UDeveloperSettings)
```

## 3. Temporal system (the core)
The two-state mechanic is the spine of the game.

- **`ETimeState { Zenith, Fall }`** and **`FTemporalStateConfig`** (per-state transform,
  visibility, material override, physics-sim flag, optional sound) live in `TemporalTypes.h`.
- **`UTemporalSubsystem : UWorldSubsystem`** — the single source of truth for the active
  state. API: `GetState()`, `RequestToggle()`, `SetState(ETimeState)`,
  `OnTimeStateChanged` (multicast). On change it: drives the transition post-process &
  Niagara, activates the matching **Data Layer** (`DL_Zenith` / `DL_Fall`), and notifies
  every registered temporal actor.
- **`ITemporalActor` + `UTemporalStateComponent`** — actors register with the subsystem
  on `BeginPlay`. On state change the component applies that state's `FTemporalStateConfig`
  (snap or interpolate). One shared mesh thus *morphs* between intact/ruined instead of
  duplicating geometry.
- **`UTemporalCausalityComponent`** — declares causal links: a change made in Zenith
  (e.g. a moved cart, an opened valve) sets a key that resolves a different result in Fall.
  Data-driven via a `UDataTable` / `UPrimaryDataAsset` so designers add puzzles without C++.
- **`UTemporalControlComponent`** (on the player) — maps input to `RequestToggle`, runs the
  "temporal **focus**" scan (highlights temporal/interactable actors), and owns the
  toggle cooldown/energy + transition camera/VFX.

### Why no GAS (for the slice)
The template uses lightweight interfaces/components, not the Gameplay Ability System.
Introducing GAS would create two parallel paradigms and slow the slice. Temporal/focus
abilities are plain components now; **GAS migration is a roadmap item** for the full game.

## 4. Puzzle / stealth / action
- **Puzzle:** `ATemporalPuzzleManager` holds the objective graph; `UPuzzleNodeComponent`
  marks gated steps. Win = "collapse averted / N citizens saved."
- **Interaction:** `UInteractableComponent` + `IInteractable` (focus → highlight → use),
  shared by levers, carts, valves, doors, and citizen NPCs.
- **Stealth (20%):** reuse `CombatAIController` + **StateTree** + **EQS** for crowd/guard
  NPCs; a `UCitizenStateComponent` switches ambient ↔ alerted and drives navigation-pressure pacing.
- **Action (10%):** Fall-state looter/hazard encounters reuse `CombatEnemy` /
  `CombatDamageable` / `CombatAttacker`. Downed → checkpoint (reuse `CombatCheckpointVolume`).
- **Save:** `UAshfallSaveGame` (+ a save subsystem) persists temporal changes, puzzle
  progress, and checkpoints.

## 5. World construction (two states)
- **World Partition** + **Data Layers** `DL_Zenith` / `DL_Fall` for state-unique set dressing.
- **Shared structural actors** carry `UTemporalStateComponent`; Data Layers carry only
  the dressing that exists in just one state.
- **Fidelity stack:** Nanite (all static meshes) · Virtual Textures · **Lumen** GI+reflections ·
  **Virtual Shadow Maps** · Sky Atmosphere + Volumetric Clouds + Height Fog · per-state
  Post-Process volumes · **Chaos Geometry Collection** fracture for transition collapses.

## 6. Asset pipeline
Host Python (`Tools/asset_pipeline/`) fetches CC0/licensed + AI-generated assets into the
gitignored `Tools/Incoming/` staging area; Unreal Python (`Tools/ue/`) imports them, builds
master materials, enables Nanite, and assembles levels. Sources: PolyHaven (CC0), Sketchfab
(CC0/CC-BY filtered), Meshy.ai, ModelsLab, Hugging Face, Freesound, ElevenLabs, Tunee.
License discipline and attributions in `docs/ASSET_LICENSES.md`.

## 7. Performance & verification
Native tooling only (VibeUE perf is Win64): `stat unit/gpu`, **Unreal Insights**, `-trace`,
`HighResShot`. Per-milestone verification: `Build.sh` returns 0 · headless Python PASS/FAIL
asserts · scripted PIE smoke tests · Zenith/Fall HighResShots · Insights trace vs. budget ·
final packaged Mac build completes the slice. Budget: 60 fps @ 1440p high-end, scalable down.
