"""
ASHFALL — build the Pompeii vertical-slice greybox (headless UE Python).

Creates /Game/Ashfall/Maps/L_Pompeii_VS: a colonnaded courtyard (House of the
Vettii) + approach street, dressed from the Kit, with two-state ATemporalProp
actors that morph Zenith<->Fall (ground material swap, standing<->toppled
columns, intact<->rubble), plus lighting, post-process, nav and player start.

Also rebuilds M_Ashfall_PBR with WORLD-ALIGNED UVs so greybox primitives tile
correctly at any scale.

Run:
  ASHFALL_LEVEL_RESULT=<file> UnrealEditor-Cmd <proj> -run=pythonscript \
      -script=Tools/ue/build_level.py -unattended -nosplash -stdout -nopause
"""
import os
import unreal

RESULT = os.environ.get("ASHFALL_LEVEL_RESULT", "/tmp/ashfall_level_result.txt")
MAP = "/Game/Ashfall/Maps/L_Pompeii_VS"
MAT_ROOT = "/Game/Ashfall/Kit/Materials"
PROPS_ROOT = "/Game/Ashfall/Kit/Props"

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
asset_lib = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
log = []
counts = {"temporal": 0, "static": 0, "light": 0, "fail": 0}


def emit(m):
    log.append(m)
    unreal.log_warning(m)
    try:  # flush incrementally so the last line survives a C++ crash
        with open(RESULT, "a") as fh:
            fh.write(m + "\n")
    except Exception:
        pass


def load(path):
    return asset_lib.load_asset(path) if asset_lib.does_asset_exist(path) else None


CUBE = load("/Engine/BasicShapes/Cube")
CYL = load("/Engine/BasicShapes/Cylinder")
PLANE = load("/Engine/BasicShapes/Plane")
MI = {p.split("/")[-1][3:]: load(p) for p in asset_lib.list_assets(MAT_ROOT)
      if p.split("/")[-1].startswith("MI_")}
emit(f"[level] kit materials: {sorted(MI.keys())}")


def vec(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def rot(pitch=0.0, yaw=0.0, roll=0.0):
    return unreal.Rotator(float(roll), float(pitch), float(yaw))


# ----------------------------------------------------------------------------
# 1) Master material with WORLD-ALIGNED UVs (so scaled primitives tile right)
# ----------------------------------------------------------------------------
def rebuild_master():
    mpath = f"{MAT_ROOT}/M_Ashfall_PBR"
    if asset_lib.does_asset_exist(mpath):
        asset_lib.delete_asset(mpath)
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_Ashfall_PBR", MAT_ROOT, unreal.Material, unreal.MaterialFactoryNew())

    def e(cls, x, y):
        return mel.create_material_expression(mat, cls, x, y)

    wp = e(unreal.MaterialExpressionWorldPosition, -1300, 0)
    tile = e(unreal.MaterialExpressionScalarParameter, -1300, 220)
    tile.set_editor_property("parameter_name", "WorldTileCm")
    tile.set_editor_property("default_value", 250.0)
    mask = e(unreal.MaterialExpressionComponentMask, -1080, 0)
    mask.set_editor_property("r", True)
    mask.set_editor_property("g", True)
    mask.set_editor_property("b", False)
    mask.set_editor_property("a", False)
    mel.connect_material_expressions(wp, "", mask, "")
    uv = e(unreal.MaterialExpressionDivide, -880, 40)
    mel.connect_material_expressions(mask, "", uv, "A")
    mel.connect_material_expressions(tile, "", uv, "B")

    def tex(name, x, y, sampler):
        p = e(unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        p.set_editor_property("parameter_name", name)
        p.set_editor_property("sampler_type", sampler)
        mel.connect_material_expressions(uv, "", p, "UVs")
        return p

    base = tex("BaseColor", -650, -350, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    norm = tex("Normal", -650, -50, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    orm = tex("ORM", -650, 250, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)

    tint = e(unreal.MaterialExpressionVectorParameter, -650, -560)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
    bmul = e(unreal.MaterialExpressionMultiply, -350, -400)
    mel.connect_material_expressions(base, "RGB", bmul, "A")
    mel.connect_material_expressions(tint, "RGB", bmul, "B")

    rscale = e(unreal.MaterialExpressionScalarParameter, -350, 300)
    rscale.set_editor_property("parameter_name", "RoughnessScale")
    rscale.set_editor_property("default_value", 1.0)
    rmul = e(unreal.MaterialExpressionMultiply, -120, 250)
    mel.connect_material_expressions(orm, "G", rmul, "A")
    mel.connect_material_expressions(rscale, "", rmul, "B")

    mel.connect_material_property(bmul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(norm, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    mel.connect_material_property(rmul, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(mat)
    asset_lib.save_loaded_asset(mat)
    emit("[level] rebuilt M_Ashfall_PBR with world-aligned UVs")


# ----------------------------------------------------------------------------
# 2) Spawn helpers
# ----------------------------------------------------------------------------
def state_config(visible=True, material=None):
    c = unreal.TemporalStateConfig()
    c.set_editor_property("visible", visible)  # UE drops the 'b' prefix from bVisible
    if material is not None:
        try:
            c.set_editor_property("material_override", material)
        except Exception:
            c.set_editor_property("material_override",
                                  unreal.SoftObjectPath(material.get_path_name()))
    return c


def place_static(mesh, loc, scale=(1, 1, 1), rotation=None, material=None, label="static"):
    if mesh is None:
        emit(f"[level] skip {label}: null mesh")
        counts["fail"] += 1
        return None
    # Use the proven spawn_actor_from_class path (spawn_actor_from_object crashes headless).
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, vec(*loc), rotation or rot())
    if not a:
        counts["fail"] += 1
        return None
    a.set_actor_label(label)
    smc = a.static_mesh_component if hasattr(a, "static_mesh_component") else a.get_editor_property("static_mesh_component")
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_static_mesh(mesh)
    a.set_actor_scale3d(vec(*scale))
    if material and smc:
        smc.set_material(0, material)
    counts["static"] += 1
    return a


def place_temporal(mesh, loc, scale=(1, 1, 1), rotation=None,
                   zenith_mat=None, fall_mat=None, zenith_vis=True, fall_vis=True, label="prop"):
    if mesh is None:
        emit(f"[level] skip {label}: null mesh")
        counts["fail"] += 1
        return None
    dbg = (counts["temporal"] == 0)  # instrument only the first temporal prop
    if dbg:
        emit("[dbg] spawn_actor_from_class TemporalProp ...")
    a = eas.spawn_actor_from_class(unreal.TemporalProp, vec(*loc), rotation or rot())
    if not a:
        counts["fail"] += 1
        return None
    if dbg:
        emit("[dbg] got actor; set label/scale")
    a.set_actor_label(label)
    a.set_actor_scale3d(vec(*scale))
    smc = a.static_mesh_component if hasattr(a, "static_mesh_component") else a.get_editor_property("static_mesh_component")
    if dbg:
        emit("[dbg] set_static_mesh ...")
    smc.set_static_mesh(mesh)
    if zenith_mat:
        if dbg:
            emit("[dbg] set_material ...")
        smc.set_material(0, zenith_mat)
    if dbg:
        emit("[dbg] get temporal component ...")
    tc = a.get_editor_property("temporal")
    if dbg:
        emit("[dbg] set zenith config ...")
    tc.set_editor_property("zenith", state_config(zenith_vis, zenith_mat))
    if dbg:
        emit("[dbg] set fall config ...")
    tc.set_editor_property("fall", state_config(fall_vis, fall_mat))
    if dbg:
        emit("[dbg] first temporal prop OK")
    counts["temporal"] += 1
    return a


def largest_mesh(folder):
    best, best_size = None, -1.0
    for p in (asset_lib.list_assets(folder, recursive=True) if asset_lib.does_directory_exist(folder) else []):
        a = load(p)
        if isinstance(a, unreal.StaticMesh):
            ext = a.get_bounds().box_extent
            size = ext.x + ext.y + ext.z
            if size > best_size:
                best, best_size = a, size
    return best


# ----------------------------------------------------------------------------
# 3) Build the level
# ----------------------------------------------------------------------------
# Fresh level each run (delete any prior, including an empty one from a failed run).
if asset_lib.does_asset_exist(MAP):
    asset_lib.delete_asset(MAP)
ok = les.new_level(MAP)
emit(f"[level] new_level({MAP}) -> {ok}")
if not ok:
    emit("[level] FATAL: new_level failed (stale map on disk?) — aborting before spawn")
    with open(RESULT, "w") as fh:
        fh.write("\n".join(log) + "\n[level] RESULT: ABORTED\n")
    raise SystemExit(0)
for nm, m in (("Cube", CUBE), ("Cylinder", CYL), ("Plane", PLANE)):
    if m is None:
        emit(f"[level] WARNING missing engine shape: {nm}")
rebuild_master()

mat_cobble = MI.get("cobblestone")
mat_ash = MI.get("ash_ground")
mat_tiles = MI.get("floor_tiles")
mat_plaster = MI.get("plaster_wall")
mat_concrete = MI.get("roman_concrete")
mat_marble = MI.get("marble")
mat_brick = MI.get("roman_brick")
mat_roof = MI.get("roof_tiles")

# Ground (60m), swaps cobblestone -> ash on Fall
place_temporal(PLANE, (0, 0, 0), (60, 60, 1),
               zenith_mat=mat_cobble, fall_mat=mat_ash, label="Ground")
# Courtyard inset floor (mosaic tiles)
place_static(PLANE, (0, 0, 2), (16, 16, 1), material=mat_tiles, label="CourtyardFloor")

# Perimeter walls of the courtyard (16m square), street gap on -X side.
WALL_H, WALL_T, HALF = 4.0, 0.4, 800.0  # metres-ish + cm half-extent
wall_defs = [
    ("Wall_N", (0, HALF, 200), (16, WALL_T, WALL_H), rot()),
    ("Wall_S", (0, -HALF, 200), (16, WALL_T, WALL_H), rot()),
    ("Wall_E", (HALF, 0, 200), (WALL_T, 16, WALL_H), rot()),
    ("Wall_Wn", (-HALF, 400, 200), (WALL_T, 8, WALL_H), rot()),   # west, north half (gap in middle)
    ("Wall_Ws", (-HALF, -400, 200), (WALL_T, 8, WALL_H), rot()),  # west, south half
]
for name, loc, scl, r in wall_defs:
    place_temporal(CUBE, loc, scl, r, zenith_mat=mat_plaster, fall_mat=mat_concrete, label=name)

emit("[level] phase: ground+floor+walls done")

# Peristyle: marble columns just inside the walls; standing in Zenith, hidden in
# Fall, with a paired toppled column appearing in Fall.
col_positions = []
for i in (-1, 0, 1):
    for side in (-1, 1):
        col_positions.append((i * 400.0, side * 600.0))
        col_positions.append((side * 600.0, i * 400.0))
seen = set()
ci = 0
for (x, y) in col_positions:
    key = (round(x), round(y))
    if key in seen:
        continue
    seen.add(key)
    ci += 1
    place_temporal(CYL, (x, y, 0), (0.6, 0.6, 4.2),
                   zenith_mat=mat_marble, fall_mat=mat_marble,
                   zenith_vis=True, fall_vis=False, label=f"Column_{ci}")
    # toppled twin (lying along +X), only in Fall
    place_temporal(CYL, (x + 120, y, 60), (0.6, 0.6, 3.0), rot(pitch=90),
                   zenith_mat=mat_marble, fall_mat=mat_marble,
                   zenith_vis=False, fall_vis=True, label=f"ColumnFallen_{ci}")

emit("[level] phase: columns done")

# Rubble piles appear only in Fall (scattered cubes near walls)
import_rubble = [(-300, 650), (350, -680), (650, 300), (-650, -250), (120, 700)]
for i, (x, y) in enumerate(import_rubble):
    place_temporal(CUBE, (x, y, 60), (1.6, 1.4, 1.0), rot(yaw=i * 23),
                   zenith_mat=mat_brick, fall_mat=mat_brick,
                   zenith_vis=False, fall_vis=True, label=f"Rubble_{i+1}")

emit("[level] phase: rubble done")

# Hero photoscan props (static): fountain centre, statue on a plinth.
fountain = largest_mesh(f"{PROPS_ROOT}/fountain")
statue = largest_mesh(f"{PROPS_ROOT}/statue")
amphora = largest_mesh(f"{PROPS_ROOT}/amphora")
vessel = largest_mesh(f"{PROPS_ROOT}/vessel")
if fountain:
    place_static(fountain, (0, 0, 5), (1, 1, 1), label="Fountain")
if statue:
    place_static(CUBE, (0, 700, 75), (1.6, 1.6, 1.5), material=mat_marble, label="StatuePlinth")
    place_static(statue, (0, 700, 150), (1, 1, 1), label="Statue")
for i, (x, y) in enumerate([(-500, 500), (480, -520), (-520, -480), (520, 480)]):
    m = amphora if i % 2 == 0 else vessel
    if m:
        place_static(m, (x, y, 5), (1, 1, 1), rot(yaw=i * 40), label=f"Vessel_{i+1}")

emit("[level] phase: hero props done")

# Approach street (cobblestone) extending -X from the courtyard gap + insula walls
place_static(PLANE, (-2200, 0, 1), (28, 8, 1), material=mat_cobble, label="Street")
place_static(CUBE, (-2200, 450, 250), (28, 0.4, 5), material=mat_plaster, label="Insula_N")
place_static(CUBE, (-2200, -450, 250), (28, 0.4, 5), material=mat_plaster, label="Insula_S")

emit("[level] phase: street done")

# ----------------------------------------------------------------------------
# 4) Lighting / atmosphere / post-process
# ----------------------------------------------------------------------------
def spawn(cls, loc, r=None, label=None):
    a = eas.spawn_actor_from_class(cls, vec(*loc), r or rot())
    if a:
        counts["light"] += 1
        if label:
            a.set_actor_label(label)
    return a


try:
    sun = spawn(unreal.DirectionalLight, (0, 0, 1500), rot(pitch=-42, yaw=-50), "Sun")
    sc = sun.get_editor_property("directional_light_component")
    sc.set_editor_property("intensity", 6.0)
    sc.set_editor_property("light_color", unreal.Color(255, 236, 210))
    sc.set_editor_property("atmosphere_sun_light", True)
    spawn(unreal.SkyAtmosphere, (0, 0, 0), label="SkyAtmosphere")
    sky = spawn(unreal.SkyLight, (0, 0, 1200), label="SkyLight")
    sky.get_editor_property("light_component").set_editor_property("real_time_capture", True)
    spawn(unreal.ExponentialHeightFog, (0, 0, 200), label="HeightFog")
    ppv = spawn(unreal.PostProcessVolume, (0, 0, 300), label="GlobalPP")
    ppv.set_editor_property("unbound", True)
except Exception as ex:
    emit(f"[level] lighting partial: {ex}")

# ----------------------------------------------------------------------------
# 5) Player start, nav, game mode, save
# ----------------------------------------------------------------------------
try:
    eas.spawn_actor_from_class(unreal.PlayerStart, vec(-1400, 0, 120), rot(yaw=0)).set_actor_label("PlayerStart")
    nav = eas.spawn_actor_from_class(unreal.NavMeshBoundsVolume, vec(-600, 0, 300))
    nav.set_actor_scale3d(vec(45, 30, 12))
    nav.set_actor_label("NavBounds")
except Exception as ex:
    emit(f"[level] start/nav partial: {ex}")

try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    ws = world.get_world_settings()
    ws.set_editor_property("default_game_mode", unreal.AshfallGameMode)
    emit("[level] world GameMode = AshfallGameMode")
except Exception as ex:
    emit(f"[level] gamemode set failed: {ex}")

emit("[level] phase: lighting+nav+gamemode done; saving ...")
les.save_current_level()
asset_lib.save_directory("/Game/Ashfall/Maps")
emit("[level] phase: saved")

total = counts["temporal"] + counts["static"]
verdict = "ALL PASS" if (counts["temporal"] >= 15 and counts["static"] >= 6 and counts["fail"] == 0) else f"CHECK {counts}"
emit(f"[level] actors: {counts}")
emit(f"[level] RESULT: {verdict}")
with open(RESULT, "w") as fh:
    fh.write("\n".join(log) + "\n")
