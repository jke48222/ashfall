# ASHFALL — Game Design Document (Vertical Slice)

> Living document. Scope = one playable Pompeii block proving the full core loop.

## 1. High concept
A time-traveler (the **Chronomason**) descends into the final hours of doomed
ancient cities and rewrites their fate by acting across two moments in time. The
slice dramatizes **Pompeii, 24 August 79 AD**, as Vesuvius wakes.

## 2. Design pillars
1. **Time is the verb.** Every meaningful action is "change the past so the future
   survives." The player toggles a location between **Zenith** and **Fall**.
2. **The city is the puzzle.** Aqueducts, streets, gates, crowds, and architecture
   are interlocking systems; collapse is a chain of failures you can interrupt.
3. **Photoreal dread.** Beauty at Zenith makes the Fall land. Light, ash, and sound
   carry the emotion more than text.
4. **Saving people, not winning fights.** Combat is a failure pressure, never the goal.

## 3. Pillar weighting
- **70% Environmental puzzle** — causal interventions across time states.
- **20% Stealth / navigation** — read crowd flow and guard patrols; pacing and tension.
- **10% Action** — if the eruption or looters corner you in the Fall, the template
  Combat variant kicks in as a fail-state to escape or be downed (checkpoint respawn).

## 4. Core loop
```
ARRIVE at a location (Fall state: a disaster in progress, people trapped)
   │
   ├─ OBSERVE   — temporal "focus" scan reveals what changed and what's interactable
   ├─ TOGGLE    — flip to Zenith (the same place, hours earlier, intact & calm)
   ├─ INTERVENE — solve a causal puzzle in Zenith (move/repair/unblock/redirect)
   ├─ TOGGLE    — return to Fall; the intervention has RIPPLED into a new outcome
   └─ RESOLVE   — the escape route now exists / the fire is starved / citizens flee
   ▼
ADVANCE to the next location; tension and ashfall rise toward the climax.
```

## 5. Flagship puzzle (slice)
**"The Blocked Stair of the House of the Vettii."**
- *Fall state:* a collapsing insula; a family is trapped on an upper floor. The
  stairway is buried under rubble and a fallen beam; fire blocks the courtyard.
- *Zenith intervention:* in the calm city, the player (a) reroutes a cart that —
  left in place — will fall and bury the stair, and (b) opens/repairs the cistern
  valve feeding the courtyard fountain.
- *Ripple to Fall:* the un-buried stair is now passable, and the charged fountain/cistern
  floods the courtyard fire, opening the escape. Citizens evacuate → objective met.
- Teaches: observe → toggle → causal change → toggle → resolve, with both a
  "structure" lever (the cart/stair) and a "flow" lever (water/fire).

## 6. Story & characters (slice)
- **The Chronomason** (player) — silent-but-expressive traveler; MetaHuman-grade.
- **Lucilla** — a Pompeiian girl who can perceive the player across time; the guide
  voice (ElevenLabs VO) and emotional anchor.
- **The Aedile's guards** — patrol the forum (stealth pressure in Zenith).
- **Vesuvius** — the antagonist; expressed through light, tremor, ash, and sound.

## 7. World (slice footprint)
One contiguous block: **forum edge → a residential street → an insula courtyard →
a temple portico**, with the bay and Vesuvius on the skyline. Two dressed states
(Zenith / Fall) over shared structural geometry.

## 8. Player abilities
| Ability | Input | Notes |
|---|---|---|
| Move / look | WASD + mouse (Enhanced Input) | from template |
| Temporal **Focus** | hold RMB | highlights temporal/interactable objects, dims rest |
| **Toggle** time state | Q | Zenith ↔ Fall at the current location (gated by zones) |
| **Interact** | E | levers, carts, valves, doors, carry/guide citizens |
| Sprint / dodge | Shift / Space | traversal + action fail-state |
| (fail-state) light melee | LMB | inherited from `ACombatCharacter` |

## 9. Difficulty & accessibility
- No instant-death; failure = downed → nearest checkpoint (reuse `CombatCheckpointVolume`).
- Focus scan + objective tracker keep the puzzle legible.
- Colorblind-safe focus highlight; subtitles for all VO; remappable input; toggle-hold options.

## 10. Win / lose (slice)
- **Win:** all targeted citizens of the block evacuated before the pyroclastic timer.
- **Lose state (soft):** caught/downed or timer expiry → checkpoint, not game-over.

## 11. Audio direction
Zenith = warm market hum, water, distant lyre. Fall = sub-bass tremor, ash hiss,
fire, panicked crowd, a single recurring lyre motif twisted minor. State-transition
stinger via MetaSounds.

## 12. Out of scope (→ ROADMAP)
Full city, multiple eras, branching narrative, GAS abilities, crowds at city scale,
console builds, multiplayer.
