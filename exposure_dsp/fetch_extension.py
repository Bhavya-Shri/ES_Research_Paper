"""Download ~15 CC extension clips into audio_in/extension/.

Does not touch the frozen 20-clip tables. Prefers Freesound preview MP3s
(Creative Commons listings), falls back to Wikimedia Commons audio.
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

from .io import load_mono, save_wav
from .paths import AUDIO_IN, ROOT

OUT = AUDIO_IN / "extension"
UA = "ES-Research-Paper-extension/1.0 (student report; digital LAeq study)"

# Freesound IDs not in the frozen 16. Preview is used (same as many CC downloads).
FREESOUND_IDS = [
    325654,
    387186,
    413480,
    439890,
    460866,
    183109,
    316678,
    345848,
    270310,
    353515,
    369515,
    416529,
    476178,
    508571,
    391539,
    242345,
    256489,
    264601,
    320181,
    332311,
    401124,
    411090,
    421188,
    632625,
    199331,
    212208,
]

WIKIMEDIA = [
    (
        "piano_fur_elise",
        "https://upload.wikimedia.org/wikipedia/commons/6/6d/Fur_Elise.ogg",
    ),
    (
        "maple_leaf_rag",
        "https://upload.wikimedia.org/wikipedia/commons/1/1f/Scott_Joplin_-_Maple_Leaf_Rag.ogg",
    ),
]


def _get(url: str, dest: Path) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.write_bytes(r.read())
        return dest.stat().st_size > 2000
    except Exception as exc:
        print(f"  fail {url}: {exc}")
        return False


def _preview_url(sound_id: int) -> str | None:
    page = f"https://freesound.org/s/{sound_id}/"
    req = urllib.request.Request(page, headers={"User-Agent": UA})
    try:
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception as exc:
        print(f"  page fail {sound_id}: {exc}")
        return None
    m = re.search(r"https://cdn\.freesound\.org/previews/\d+/\d+_[^\"']+\.(?:mp3|ogg)", html)
    return m.group(0) if m else None


def _ffmpeg_wav(src: Path, dest: Path, fs: float = 48000.0) -> bool:
    import shutil
    import subprocess

    ff = shutil.which("ffmpeg")
    if not ff:
        return False
    cmd = [ff, "-y", "-i", str(src), "-ac", "1", "-ar", str(int(fs)), str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and dest.exists()


def _to_wav(src: Path, stem: str, fs: float = 48000.0) -> Path | None:
    out = OUT / f"{stem}.wav"
    try:
        x, _ = load_mono(src, target_fs=fs)
    except Exception:
        if src.suffix.lower() != ".wav" and _ffmpeg_wav(src, out, fs):
            try:
                x, _ = load_mono(out, target_fs=fs)
            except Exception as exc:
                print(f"  decode fail {src.name}: {exc}")
                return None
        else:
            print(f"  decode fail {src.name}")
            return None
    if len(x) < int(0.4 * fs):
        print(f"  too short {src.name}")
        return None
    out = OUT / f"{stem}.wav"
    save_wav(out, x, fs)
    return out


def fetch(n_target: int = 15) -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    got: list[Path] = []
    got = list(OUT.glob("ext_*.wav"))
    for sid in FREESOUND_IDS:
        if len(got) >= n_target:
            break
        dest = OUT / f"ext_{sid}.wav"
        if dest.exists():
            continue
        print(f"[freesound {sid}]")
        url = _preview_url(sid)
        if not url:
            continue
        tmp = OUT / f"_tmp_{sid}{Path(url).suffix}"
        if not _get(url, tmp):
            continue
        wav = _to_wav(tmp, f"ext_{sid}")
        tmp.unlink(missing_ok=True)
        if wav is not None:
            print(f"  wrote {wav.name}")
            got.append(wav)
    for stem, url in WIKIMEDIA:
        if len(got) >= n_target:
            break
        print(f"[wikimedia {stem}]")
        tmp = OUT / f"_tmp_{stem}{Path(url).suffix}"
        if not _get(url, tmp):
            continue
        wav = _to_wav(tmp, f"ext_{stem}")
        tmp.unlink(missing_ok=True)
        if wav is not None:
            print(f"  wrote {wav.name}")
            got.append(wav)
    print(f"extension clips: {len(got)} in {OUT}")
    return got


if __name__ == "__main__":
    fetch()
