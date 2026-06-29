"""
ASHFALL — import staged Sketchfab glTF props into the project with Nanite.

Reads Tools/Incoming/sketchfab/manifest.json, imports each scene.gltf into
/Game/Ashfall/Kit/Props/<label>, then enables Nanite on the resulting static
meshes (these are dense photoscans — exactly what Nanite is for).

Run:
  ASHFALL_MODELS_RESULT=<file> UnrealEditor-Cmd <proj> -run=pythonscript \
      -script=Tools/ue/import_models.py -unattended -nosplash -stdout -nopause
"""
import json
import os
import unreal

PROJECT_DIR = unreal.SystemLibrary.get_project_directory()
INCOMING = os.path.join(PROJECT_DIR, "Tools", "Incoming", "sketchfab")
MANIFEST = os.path.join(INCOMING, "manifest.json")
RESULT = os.environ.get("ASHFALL_MODELS_RESULT", "/tmp/ashfall_models_result.txt")
PROPS_ROOT = "/Game/Ashfall/Kit/Props"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_lib = unreal.EditorAssetLibrary
log = []


def emit(m):
    log.append(m)
    unreal.log_warning(m)


def enable_nanite(mesh):
    try:
        ses = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        ns = unreal.MeshNaniteSettings()
        ns.set_editor_property("enabled", True)
        ses.set_nanite_settings(mesh, ns, apply_changes=True)
        return True
    except Exception as e1:
        try:
            ns = mesh.get_editor_property("nanite_settings")
            ns.set_editor_property("enabled", True)
            mesh.set_editor_property("nanite_settings", ns)
            return True
        except Exception as e2:
            emit(f"[models]   nanite FAIL: {e1} | {e2}")
            return False


def import_gltf(scene_path, dest):
    task = unreal.AssetImportTask()
    task.filename = scene_path
    task.destination_path = dest
    task.automated = True
    task.save = True
    task.replace_existing = True
    asset_tools.import_asset_tasks([task])
    return list(task.get_objects())


manifest = json.loads(open(MANIFEST).read()) if os.path.exists(MANIFEST) else []
emit(f"[models] manifest: {len(manifest)} models")

total_meshes = 0
nanite_ok = 0
for entry in manifest:
    label = entry["label"]
    scene = os.path.join(INCOMING, entry["scene"])
    if not os.path.exists(scene):
        emit(f"[models] MISSING {scene}")
        continue
    dest = f"{PROPS_ROOT}/{label}"
    emit(f"[models] importing {label} <- {entry.get('name','')[:40]} ({entry.get('license')})")
    try:
        objs = import_gltf(scene, dest)
    except Exception as e:
        emit(f"[models]   import FAIL {label}: {e}")
        continue
    # Enable Nanite on every StaticMesh produced (from results + folder scan).
    meshes = [o for o in objs if isinstance(o, unreal.StaticMesh)]
    for path in (asset_lib.list_assets(dest, recursive=True) if asset_lib.does_directory_exist(dest) else []):
        a = asset_lib.load_asset(path)
        if isinstance(a, unreal.StaticMesh) and a not in meshes:
            meshes.append(a)
    for m in meshes:
        total_meshes += 1
        if enable_nanite(m):
            nanite_ok += 1
        asset_lib.save_loaded_asset(m)
    emit(f"[models]   {label}: {len(meshes)} static mesh(es)")

verdict = "ALL PASS" if (total_meshes >= 5 and nanite_ok == total_meshes) else \
    f"CHECK (meshes={total_meshes}, nanite_ok={nanite_ok})"
emit(f"[models] meshes={total_meshes} nanite_enabled={nanite_ok}")
emit(f"[models] RESULT: {verdict}")
with open(RESULT, "w") as fh:
    fh.write("\n".join(log) + "\n")
