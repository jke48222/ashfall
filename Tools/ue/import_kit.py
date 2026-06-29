"""
ASHFALL — import the staged PolyHaven kit into the project (headless UE Python).

Reads Tools/Incoming/polyhaven/manifest.json and:
  1. imports each texture with correct sRGB + compression
     (BaseColor sRGB; Normal=TC_NORMALMAP; ORM=TC_MASKS linear; Height linear),
  2. imports the HDRIs,
  3. builds a parametric master material  M_Ashfall_PBR,
  4. creates one material instance  MI_<label>  per material set,
  5. saves everything and writes a result file.

Run:
  ASHFALL_KIT_RESULT=<file> UnrealEditor-Cmd <proj> -run=pythonscript \
      -script=Tools/ue/import_kit.py -unattended -nosplash -stdout -nopause
"""
import json
import os
import unreal

PROJECT_DIR = unreal.SystemLibrary.get_project_directory()
INCOMING = os.path.join(PROJECT_DIR, "Tools", "Incoming", "polyhaven")
MANIFEST = os.path.join(INCOMING, "manifest.json")
RESULT = os.environ.get("ASHFALL_KIT_RESULT", "/tmp/ashfall_kit_result.txt")

KIT = "/Game/Ashfall/Kit"
TEX_ROOT = f"{KIT}/Textures"
HDRI_ROOT = f"{KIT}/HDRI"
MAT_ROOT = f"{KIT}/Materials"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_lib = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
log = []


def emit(msg):
    log.append(msg)
    unreal.log_warning(msg)


def import_texture(src_path, dest_dir, asset_name):
    task = unreal.AssetImportTask()
    task.filename = src_path
    task.destination_path = dest_dir
    task.destination_name = asset_name
    task.automated = True
    task.save = True
    task.replace_existing = True
    asset_tools.import_asset_tasks([task])
    paths = list(task.get_objects())
    return paths[0] if paths else asset_lib.load_asset(f"{dest_dir}/{asset_name}")


def configure_texture(tex, kind):
    if not tex:
        return
    if kind == "diffuse":
        tex.set_editor_property("srgb", True)
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
    elif kind == "normal":
        tex.set_editor_property("srgb", False)
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    elif kind == "arm":
        tex.set_editor_property("srgb", False)
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    elif kind == "height":
        tex.set_editor_property("srgb", False)
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
    unreal.EditorAssetLibrary.save_loaded_asset(tex)


# --- 1) Textures -----------------------------------------------------------
manifest = json.loads(open(MANIFEST).read())
textures = [e for e in manifest if e.get("type") == "texture"]
hdris = [e for e in manifest if e.get("type") == "hdri"]
emit(f"[kit] manifest: {len(textures)} textures, {len(hdris)} hdris")

imported = {}  # label -> {kind: Texture2D}
for entry in textures:
    label = entry["label"]
    maps = entry.get("maps", {})
    dest = f"{TEX_ROOT}/{label}"
    imported[label] = {}
    for kind, fname in maps.items():
        src = os.path.join(INCOMING, "textures", label, fname)
        if not os.path.exists(src):
            emit(f"[kit] MISSING {src}")
            continue
        tex = import_texture(src, dest, f"T_{label}_{kind}")
        configure_texture(tex, kind)
        imported[label][kind] = tex
    emit(f"[kit] imported {label}: {sorted(imported[label].keys())}")

# --- 2) HDRIs --------------------------------------------------------------
for entry in hdris:
    src = os.path.join(INCOMING, "hdri", entry["file"])
    if os.path.exists(src):
        import_texture(src, HDRI_ROOT, f"HDR_{entry['label']}")
        emit(f"[kit] imported HDRI {entry['label']}")


# --- 3) Master material ----------------------------------------------------
def build_master():
    mpath = f"{MAT_ROOT}/M_Ashfall_PBR"
    if asset_lib.does_asset_exist(mpath):
        asset_lib.delete_asset(mpath)  # clean rebuild
    mat = asset_tools.create_asset("M_Ashfall_PBR", MAT_ROOT, unreal.Material,
                                   unreal.MaterialFactoryNew())

    def expr(cls, x, y):
        return mel.create_material_expression(mat, cls, x, y)

    # UV tiling
    texcoord = expr(unreal.MaterialExpressionTextureCoordinate, -1100, 0)
    tiling = expr(unreal.MaterialExpressionScalarParameter, -1100, 150)
    tiling.set_editor_property("parameter_name", "Tiling")
    tiling.set_editor_property("default_value", 1.0)
    uv_mul = expr(unreal.MaterialExpressionMultiply, -900, 50)
    mel.connect_material_expressions(texcoord, "", uv_mul, "A")
    mel.connect_material_expressions(tiling, "", uv_mul, "B")

    def tex_param(name, x, y, sampler):
        p = expr(unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        p.set_editor_property("parameter_name", name)
        p.set_editor_property("sampler_type", sampler)
        mel.connect_material_expressions(uv_mul, "", p, "UVs")
        return p

    base = tex_param("BaseColor", -650, -350, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    norm = tex_param("Normal", -650, -50, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    orm = tex_param("ORM", -650, 250, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)

    # Tint multiply on base color
    tint = expr(unreal.MaterialExpressionVectorParameter, -650, -550)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
    base_mul = expr(unreal.MaterialExpressionMultiply, -350, -400)
    mel.connect_material_expressions(base, "RGB", base_mul, "A")
    mel.connect_material_expressions(tint, "RGB", base_mul, "B")

    # Roughness scale
    rscale = expr(unreal.MaterialExpressionScalarParameter, -350, 300)
    rscale.set_editor_property("parameter_name", "RoughnessScale")
    rscale.set_editor_property("default_value", 1.0)
    rough_mul = expr(unreal.MaterialExpressionMultiply, -120, 250)
    mel.connect_material_expressions(orm, "G", rough_mul, "A")
    mel.connect_material_expressions(rscale, "", rough_mul, "B")

    mel.connect_material_property(base_mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(norm, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    mel.connect_material_property(rough_mul, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)

    mel.recompile_material(mat)
    asset_lib.save_loaded_asset(mat)
    return mat


master = build_master()
emit("[kit] master material M_Ashfall_PBR ready")


# --- 4) Material instances -------------------------------------------------
def make_instance(label, maps):
    name = f"MI_{label}"
    if asset_lib.does_asset_exist(f"{MAT_ROOT}/{name}"):
        mic = asset_lib.load_asset(f"{MAT_ROOT}/{name}")
    else:
        mic = asset_tools.create_asset(name, MAT_ROOT, unreal.MaterialInstanceConstant,
                                       unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mic, master)
    pmap = {"diffuse": "BaseColor", "normal": "Normal", "arm": "ORM"}
    for kind, param in pmap.items():
        tex = maps.get(kind)
        if tex:
            mel.set_material_instance_texture_parameter_value(mic, param, tex)
    asset_lib.save_loaded_asset(mic)
    return mic


mi_count = 0
for label, maps in imported.items():
    if maps.get("diffuse"):
        make_instance(label, maps)
        mi_count += 1
emit(f"[kit] created {mi_count} material instances")

# --- result ----------------------------------------------------------------
tex_assets = asset_lib.list_assets(TEX_ROOT, recursive=True) if asset_lib.does_directory_exist(TEX_ROOT) else []
mat_assets = asset_lib.list_assets(MAT_ROOT, recursive=True) if asset_lib.does_directory_exist(MAT_ROOT) else []
verdict = "ALL PASS" if (mi_count >= 8 and len(tex_assets) >= 30) else f"CHECK (mi={mi_count}, tex={len(tex_assets)})"
emit(f"[kit] textures={len(tex_assets)} materials={len(mat_assets)} instances={mi_count}")
emit(f"[kit] RESULT: {verdict}")
with open(RESULT, "w") as fh:
    fh.write("\n".join(log) + "\n")
