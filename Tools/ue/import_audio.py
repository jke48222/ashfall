"""
ASHFALL — import the staged WAV audio into the project (headless UE Python).

Imports Tools/Incoming/audio/{vo,sfx}/*.wav into /Game/Ashfall/Audio/{VO,SFX}
as SoundWaves; marks the ambient beds (amb_*/fall_*) looping.

Run:
  ASHFALL_AUDIO_RESULT=<file> UnrealEditor-Cmd <proj> -run=pythonscript \
      -script=Tools/ue/import_audio.py -unattended -nosplash -stdout -nopause
"""
import os
import unreal

PROJECT_DIR = unreal.SystemLibrary.get_project_directory()
INCOMING = os.path.join(PROJECT_DIR, "Tools", "Incoming", "audio")
RESULT = os.environ.get("ASHFALL_AUDIO_RESULT", "/tmp/ashfall_audio_result.txt")
AUDIO_ROOT = "/Game/Ashfall/Audio"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_lib = unreal.EditorAssetLibrary
log = []


def emit(m):
    log.append(m)
    unreal.log_warning(m)


def import_wav(src, dest_dir, name):
    task = unreal.AssetImportTask()
    task.filename = src
    task.destination_path = dest_dir
    task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = True
    asset_tools.import_asset_tasks([task])
    objs = list(task.get_objects())
    return objs[0] if objs else asset_lib.load_asset(f"{dest_dir}/{name}")


count = 0
for sub, folder in (("vo", "VO"), ("sfx", "SFX")):
    src_dir = os.path.join(INCOMING, sub)
    if not os.path.isdir(src_dir):
        continue
    for fn in sorted(os.listdir(src_dir)):
        if not fn.lower().endswith(".wav"):
            continue
        name = os.path.splitext(fn)[0]
        sw = import_wav(os.path.join(src_dir, fn), f"{AUDIO_ROOT}/{folder}", name)
        if sw and isinstance(sw, unreal.SoundWave):
            # Loop the ambient/atmosphere beds; one-shots (vo, stinger) stay non-looping.
            loop = any(k in name.lower() for k in ("amb_", "ash_wind", "fire_crackle", "rumble"))
            try:
                sw.set_editor_property("looping", loop)
                asset_lib.save_loaded_asset(sw)
            except Exception as e:
                emit(f"  [skip loop] {name}: {e}")
            count += 1
            emit(f"[audio] imported {folder}/{name} (loop={loop})")

emit(f"[audio] RESULT: imported {count} sounds")
with open(RESULT, "w") as fh:
    fh.write("\n".join(log) + "\n")
