import subprocess
from pathlib import Path

import imageio_ffmpeg

ff = imageio_ffmpeg.get_ffmpeg_exe()
demo_dir = Path(__file__).resolve().parent
src = next(p for p in demo_dir.glob("*.mp4") if "linkedin" not in p.name.lower())
out = demo_dir / "_thumbs"
out.mkdir(exist_ok=True)
for old in out.glob("*.png"):
    old.unlink()
cmd = [
    ff,
    "-y",
    "-i",
    str(src),
    "-vf",
    "fps=1/8,scale=960:-2",
    str(out / "t%03d.png"),
]
print(" ".join(cmd))
subprocess.check_call(cmd)
print("frames", len(list(out.glob("*.png"))))
