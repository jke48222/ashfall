"""
ASHFALL — M4 validation (headless).

Exercises the full causal-ripple gameplay loop through the Blueprint/Python
library: a Zenith intervention (causal flag) survives a toggle to Fall, then
rescuing CitizensToSave citizens flips the objective to Won.

Run:
  ASHFALL_M4_RESULT=<file> UnrealEditor-Cmd <proj> -run=pythonscript \
      -script=Tools/ue/validate_m4.py -unattended -nosplash -nullrhi -stdout -nopause
Success marker: [M4] RESULT: ALL PASS
"""
import os
import unreal

RESULT = os.environ.get("ASHFALL_M4_RESULT", "/tmp/ashfall_m4_result.txt")
_lines, _fails = [], []


def expect(name, cond):
    s = "PASS" if cond else "FAIL"
    msg = f"[M4] {s} : {name}"
    _lines.append(msg)
    (unreal.log if cond else unreal.log_warning)(msg)
    if not cond:
        _fails.append(name)


def registered(path):
    try:
        return unreal.find_object(None, path) is not None
    except Exception:
        return False


# 1) Registration of M4 types.
for p in ("/Script/game.InteractableComponent", "/Script/game.Interactable",
          "/Script/game.AshfallObjectiveSubsystem", "/Script/game.EObjectiveState"):
    expect(f"registered {p.split('.')[-1]}", registered(p))

# 2) World + library.
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
expect("editor world", world is not None)
lib = unreal.AshfallTemporalLibrary

# 3) Objective baseline (CitizensToSave default = 6).
total = lib.get_citizens_total(world)
expect("objective total >= 1", total >= 1)
expect("objective starts at 0 saved", lib.get_citizens_saved(world) == 0)
expect("objective not won at start", lib.is_objective_won(world) is False)

# 4) Causal ripple: Zenith intervention survives a toggle to Fall.
lib.set_time_state(world, unreal.TimeState.ZENITH)
lib.set_causal_flag(world, "Vettii.StairCleared", True)
lib.toggle_time_state(world)  # -> Fall
expect("in Fall after toggle", lib.get_time_state(world) == unreal.TimeState.FALL)
expect("causal flag survived toggle", lib.has_causal_flag(world, "Vettii.StairCleared") is True)

# 5) Rescue loop -> objective Won at the target.
for i in range(total):
    lib.save_citizen(world)
    expect(f"saved count == {i+1}", lib.get_citizens_saved(world) == i + 1)
expect("objective WON at target", lib.is_objective_won(world) is True)

# 6) Saved count is clamped at total.
lib.save_citizen(world)
expect("saved clamped at total", lib.get_citizens_saved(world) == total)

verdict = "ALL PASS" if not _fails else f"FAIL ({len(_fails)}): {_fails}"
_lines.append(f"[M4] RESULT: {verdict}")
unreal.log_warning(f"[M4] RESULT: {verdict}")
with open(RESULT, "w") as fh:
    fh.write("\n".join(_lines) + "\n")
