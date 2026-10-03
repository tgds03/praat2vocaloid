from pathlib import Path
import os
import shutil
import subprocess

DIR = Path(__file__).resolve().parent
SCRIPT = DIR / "extract.praat"

CANDIDATES = [
    "/Applications/Praat.app/Contents/MacOS/Praat",
    r"C:\Program Files\Praat.exe",
    r"C:\Program Files\Praat\Praat.exe",
]

def find_praat(explicit=None):
    if explicit is not None:
        if not Path(explicit).is_file():
            raise RuntimeError(f"Can not find praat executable at {explicit}")
        return str(explicit)
    env_path = os.environ.get("PRAAT_PATH")
    if env_path and Path(env_path).is_file():
        return env_path
    for name in ("praat", "Praat"):
        found = shutil.which(name)
        if found:
            return found
    for path in CANDIDATES:
        if Path(path).is_file():
            return path
    raise RuntimeError(
        "Can not find praat. Install it (https://www.fon.hum.uva.nl/praat/, "
        "or `brew install --cask praat` on macOS), "
        "or pass its path with --praat or the PRAAT_PATH environment variable.")

def extract(audio_path, praat_path=None, time_step=0, pitch_floor=75, pitch_ceiling=600):
    audio_path = Path(audio_path).resolve()
    if not audio_path.is_file():
        raise RuntimeError(f"Can not find audio file {audio_path}")
    praat = find_praat(praat_path)
    cmd = [praat, "--run", str(SCRIPT), str(audio_path),
           str(time_step), str(pitch_floor), str(pitch_ceiling)]
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"Praat failed on {audio_path}:\n{result.stderr.strip()}")

    data = {"time": [], "f0": [], "intensity": []}
    lines = result.stdout.splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        time_value, f0_value, intensity_value = line.split('\t')
        data["time"].append(float(time_value))
        data["f0"].append(float(f0_value))
        data["intensity"].append(float(intensity_value))
    return data
