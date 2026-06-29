# ASHFALL — Asset Licenses & Attributions

**Policy:** only **CC0**, **CC-BY** (attributed below), or **self-generated** assets ship
in `Content/`. AI-generated assets (Meshy, ModelsLab, Hugging Face, ElevenLabs, Tunee) are
original outputs created for this project. Epic-provided template/Mannequin content is used
under the Unreal Engine EULA. This file is updated whenever an asset is imported (M2+).

## Engine / template content
| Asset | Source | License |
|---|---|---|
| Third-Person template, Mannequins (Manny/Quinn), template anims/materials | Epic Games (project template) | Unreal Engine EULA |

## CC0 sources (no attribution legally required; recorded for provenance)

All assets below are **CC0 1.0** from [PolyHaven](https://polyhaven.com), imported
into `/Game/Ashfall/Kit` as `MI_<label>` material instances + `HDR_<label>` skies.
Provenance mirrored in `Tools/Incoming/polyhaven/manifest.json`.

| Material instance | PolyHaven asset | Maps |
|---|---|---|
| `MI_marble` | `marble_cliff_03` | BaseColor / Normal / ORM / Height |
| `MI_plaster_wall` | `painted_plaster_wall` | BaseColor / Normal / ORM / Height |
| `MI_roman_brick` | `red_brick` | BaseColor / Normal / ORM / Height |
| `MI_cobblestone` | `floor_pattern_02` | BaseColor / Normal / ORM / Height |
| `MI_floor_tiles` | `tiled_floor_001` | BaseColor / Normal / ORM / Height |
| `MI_roman_concrete` | `beige_wall_001` | BaseColor / Normal / ORM / Height |
| `MI_wood_planks` | `wood_planks_dirt` | BaseColor / Normal / ORM / Height |
| `MI_roof_tiles` | `clay_roof_tiles_02` | BaseColor / Normal / ORM / Height |
| `MI_ash_ground` | `burned_ground_01` | BaseColor / Normal / ORM / Height |
| `HDR_zenith_sky` | `lonely_road_afternoon_puresky` | 4K equirectangular HDRI |
| `HDR_fall_sky` | `quarry_cloudy` | 4K equirectangular HDRI |

## CC0 models (Sketchfab — no attribution required)
| Prop set | Model | Author | Source |
|---|---|---|---|
| `Props/statue` | Julius Cäsar | noe-3d.at | https://sketchfab.com/3d-models/802edad501a94f9c99b84c4c33d376b7 |

## CC-BY sources (attribution REQUIRED — keep current)
Imported into `/Game/Ashfall/Kit/Props/<set>` as Nanite static meshes. Each model
is **CC-BY 4.0**; the credits below must ship with the game.

| Prop set | Model | Author | Source |
|---|---|---|---|
| `Props/column` | Greek/Roman Corinthian Column | ChrisCLP | https://sketchfab.com/3d-models/c6df8ee1fe234ad4bdffae759ccc3460 |
| `Props/amphora` | Greek Amphoras Set 02 | cebraVFX | https://sketchfab.com/3d-models/e114a15c0857459786e351d8a39f7036 |
| `Props/capital` | Modular Columns Library | TotorLeJaune | https://sketchfab.com/3d-models/c0393908ae8243bfac1ae331e6156cb1 |
| `Props/fountain` | Fountain of Peirene — Corinth (CyArk dataset) | Vasilis Haroupas | https://sketchfab.com/3d-models/47aba312ea00406d84b1b90f216da90e |
| `Props/vessel` | Assorted Old Pots | Kigha | https://sketchfab.com/3d-models/7795c6a5fa144bfcb1c33041c71eab00 |

## Self-generated (AI) assets
| Asset | Generator | Notes |
|---|---|---|
| _none yet_ | Meshy.ai / ModelsLab / HF / ElevenLabs / Tunee | added in the M5 art/FX/audio pass |

## Audio
| Asset | Source | License |
|---|---|---|
| _pending M2_ | Freesound (CC0/CC-BY filtered) · ElevenLabs (VO) · Tunee (score) | per-item below |

> Each fetcher writes a per-download manifest (author, URL, license, date) into
> `Tools/Incoming/<source>/manifest.json`; this table is reconciled from those manifests.
