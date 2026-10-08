"""Build a 60-90s LinkedIn MP4 from the local demo recording."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg
except ImportError:
    sys.exit("Installez imageio-ffmpeg : python -m pip install imageio-ffmpeg")

DEMO = Path(__file__).resolve().parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SRC = next(p for p in DEMO.glob("*.mp4") if "linkedin" not in p.name.lower() and not p.name.startswith("_"))
OUT = DEMO / "demo-projet2-linkedin.mp4"
WORK = DEMO / "_linkedin_build"
TITLE_PNG = WORK / "title.png"
TITLE_MP4 = WORK / "title.mp4"
CONCAT = WORK / "concat.txt"


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd[:8]), "...")
    subprocess.check_call(cmd)


def probe(path: Path) -> str:
    result = subprocess.run(
        [FFMPEG, "-i", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stderr


def make_title_png() -> None:
    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 54)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 36)
        font_small = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 28)
    except OSError:
        font_title = font_sub = font_small = ImageFont.load_default()

    lines = [
        (font_title, "Projet 2 — Prédiction du salaire", (248, 250, 252)),
        (font_sub, "d'un développeur selon ses compétences", (226, 232, 240)),
        (font_small, "XGBoost  ·  MAE 22 649 USD  ·  R² 0,36  ·  app locale", (125, 211, 252)),
    ]
    y = 390
    for font, text, color in lines:
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), text, font=font, fill=color)
        y += (bbox[3] - bbox[1]) + 28
    img.save(TITLE_PNG)


def clip(name: str, start: float, duration: float) -> Path:
    dest = WORK / name
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        "drawtext=fontfile='C\\:/Windows/Fonts/segoeui.ttf':"
        "text='XGBoost  ·  MAE 22 649 USD  ·  R² 0,36  ·  app locale':"
        "fontcolor=white:fontsize=28:box=1:boxcolor=0x0f172acc:"
        "boxborderw=12:x=(w-text_w)/2:y=h-80"
    )
    cmd = [
        FFMPEG, "-y",
        "-ss", str(start),
        "-t", str(duration),
        "-i", str(SRC),
        "-vf", vf,
        "-r", "30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-an",
        str(dest),
    ]
    try:
        run(cmd)
    except subprocess.CalledProcessError:
        cmd = [
            FFMPEG, "-y",
            "-ss", str(start),
            "-t", str(duration),
            "-i", str(SRC),
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-r", "30",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",
            str(dest),
        ]
        run(cmd)
    return dest


def main() -> None:
    WORK.mkdir(exist_ok=True)
    print("SRC", SRC)
    print(probe(SRC))

    # Default cuts from a typical ~5 min walkthrough of the 4 screens.
    # Adjust after probing if the recording is shorter.
    segments = [
        ("pred.mp4", 8.0, 32.0),
        ("compare.mp4", 95.0, 18.0),
        ("dash.mp4", 170.0, 18.0),
        ("about.mp4", 250.0, 6.0),
    ]

    make_title_png()
    run([
        FFMPEG, "-y",
        "-loop", "1",
        "-t", "3",
        "-i", str(TITLE_PNG),
        "-f", "lavfi",
        "-t", "3",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-shortest",
        str(TITLE_MP4),
    ])

    parts = [TITLE_MP4]
    for name, start, duration in segments:
        parts.append(clip(name, start, duration))

    CONCAT.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    run([
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(CONCAT),
        "-f", "lavfi",
        "-t", "90",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        "-movflags", "+faststart",
        str(OUT),
    ])
    print("OUT", OUT)
    print("SIZE_MB", round(OUT.stat().st_size / 1024 / 1024, 2))
    print(probe(OUT))


if __name__ == "__main__":
    main()
