"""
ASHFALL — M1 validation (headless, file-output).

Asserts (a) the temporal C++ types are registered with the engine, (b) the
Zenith<->Fall state machine and causal-flag store behave, driving them through
the Blueprint/Python library in the editor world. Writes a result file so the
outcome is captured deterministically (UE only logs unreal.log*, not print()).

Run:
  ASHFALL_M1_RESULT=<file> UnrealEditor-Cmd <proj> -run=pythonscript \
      -script=<abs path> -unattended -nosplash -nullrhi -stdout -nopause

Success marker in the result file:  [M1] RESULT: ALL PASS
"""
import os
import unreal

RESULT_PATH = os.environ.get("ASHFALL_M1_RESULT", "/tmp/ashfall_m1_result.txt")

_lines = []
_fails = []


def expect(name, cond):
    status = "PASS" if cond else "FAIL"
    msg = f"[M1] {status} : {name}"
    _lines.append(msg)
    (unreal.log if cond else unreal.log_warning)(msg)
    if not cond:
        _fails.append(name)


def registered(path):
    try:
        return unreal.find_object(None, path) is not None
    except Exception:
        return False


# 1) Ground-truth engine registration (independent of Python attribute quirks).
expect("UEnum  ETimeState registered",          registered("/Script/game.ETimeState"))
expect("UStruct TemporalStateConfig registered", registered("/Script/game.TemporalStateConfig"))
expect("UClass  AshfallSettings registered",     registered("/Script/game.AshfallSettings"))
expect("UClass  TemporalSubsystem registered",   registered("/Script/game.TemporalSubsystem"))
expect("UClass  AshfallCharacter registered",    registered("/Script/game.AshfallCharacter"))

# 2) Python attribute visibility. NB: UE strips the leading 'E' from enum names,
#    so ETimeState is exposed to Python as unreal.TimeState.
expect("python unreal.TimeState present",            hasattr(unreal, "TimeState"))
expect("python unreal.AshfallTemporalLibrary present", hasattr(unreal, "AshfallTemporalLibrary"))

# 3) State machine + causality via the library.
ZENITH = unreal.TimeState.ZENITH
FALL = unreal.TimeState.FALL

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
expect("editor world available", world is not None)

lib = unreal.AshfallTemporalLibrary
sub = lib.get_temporal_subsystem(world) if world else None
expect("temporal subsystem resolved", sub is not None)

if sub is not None:
    s0 = lib.get_time_state(world)
    s1 = lib.toggle_time_state(world)
    s2 = lib.toggle_time_state(world)
    expect("initial state == Zenith", s0 == ZENITH)
    expect("toggle flips to Fall", s1 == FALL)
    expect("toggle restores Zenith", s2 == ZENITH)

    lib.set_causal_flag(world, "Vettii.StairCleared", True)
    expect("causal flag set", lib.has_causal_flag(world, "Vettii.StairCleared") is True)
    lib.set_causal_flag(world, "Vettii.StairCleared", False)
    expect("causal flag cleared", lib.has_causal_flag(world, "Vettii.StairCleared") is False)

verdict = "ALL PASS" if not _fails else f"FAIL ({len(_fails)}): {_fails}"
_lines.append(f"[M1] RESULT: {verdict}")
unreal.log_warning(f"[M1] RESULT: {verdict}")

with open(RESULT_PATH, "w") as fh:
    fh.write("\n".join(_lines) + "\n")
