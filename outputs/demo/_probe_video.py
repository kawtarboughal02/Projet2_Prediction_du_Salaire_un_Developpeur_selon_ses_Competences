import os
import subprocess
from pathlib import Path

import imageio_ffmpeg

ff = imageio_ffmpeg.get_ffmpeg_exe()
demo_dir = Path(__file__).resolve().parent
src = next(p for p in demo_dir.glob("*.mp4") if "linkedin" not in p.name.lower())
print("FFMPEG", ff)
print("SRC", src)
print("SIZE_MB", round(src.stat().st_size / 1024 / 1024, 2))
result = subprocess.run([ff, "-i", str(src)], capture_output=True, text=True, encoding="utf-8", errors="replace")
print(result.stderr)
