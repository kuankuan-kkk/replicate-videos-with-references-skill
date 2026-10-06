#!/usr/bin/env python3
"""Inspect a video with ffprobe and emit compact JSON evidence."""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=pathlib.Path)
    args = parser.parse_args()
    if not args.video.is_file():
        raise SystemExit(f"video not found: {args.video}")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise SystemExit("ffprobe is not available")
    cmd = [
        ffprobe, "-v", "error", "-show_entries",
        "format=duration,format_name,size:stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,duration,rotation:stream_tags=rotate",
        "-of", "json", str(args.video),
    ]
    try:
        completed = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        raise SystemExit('metadata inspection timed out; not a usable-source verification')
    if completed.returncode:
        raise SystemExit(completed.stderr.strip() or "ffprobe failed")
    data = json.loads(completed.stdout)
    data["source_file"] = str(args.video.resolve())
    data["metadata_only"] = True
    data["full_decode_verified"] = False
    data["semantic_observation_complete"] = False
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
