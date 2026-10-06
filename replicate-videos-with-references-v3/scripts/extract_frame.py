#!/usr/bin/env python3
"""Extract a finite in-range frame; verify existence, readability and size."""
import argparse,json,math,pathlib,shutil,subprocess
def main():
    p=argparse.ArgumentParser();p.add_argument('video',type=pathlib.Path);p.add_argument('time_seconds',type=float);p.add_argument('output',type=pathlib.Path);a=p.parse_args()
    if not a.video.is_file():p.error('video missing')
    if not math.isfinite(a.time_seconds) or a.time_seconds<0:p.error('time must be finite and nonnegative')
    if a.output.exists():p.error('will not overwrite existing output')
    ffmpeg,ffprobe=shutil.which('ffmpeg'),shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:p.error('ffmpeg and ffprobe required for verified extraction')
    try:
        probe=subprocess.run([ffprobe,'-v','error','-show_entries','format=duration','-of','json',str(a.video)],check=True,capture_output=True,text=True,timeout=30)
        duration=float(json.loads(probe.stdout)['format']['duration'])
        if not math.isfinite(duration) or not 0<=a.time_seconds<duration:p.error('time is outside source duration')
        a.output.parent.mkdir(parents=True,exist_ok=True)
        r=subprocess.run([ffmpeg,'-nostdin','-n','-v','error','-ss',str(a.time_seconds),'-i',str(a.video),'-frames:v','1',str(a.output)],capture_output=True,text=True,timeout=120)
        if r.returncode:raise ValueError(r.stderr.strip() or 'extraction failed')
        if not a.output.is_file() or a.output.stat().st_size==0:raise ValueError('no frame produced')
        from PIL import Image
        with Image.open(a.output) as im:im.verify()
    except (OSError,ValueError,KeyError,subprocess.SubprocessError) as exc:p.error(str(exc))
    print(a.output.resolve());return 0
if __name__=='__main__':raise SystemExit(main())
