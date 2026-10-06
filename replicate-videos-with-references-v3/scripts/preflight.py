#!/usr/bin/env python3
"""Separate runtime tools, per-file decode, semantic coverage and editor capability."""
import argparse,importlib.util,json,pathlib,shutil,subprocess
def main():
    p=argparse.ArgumentParser();p.add_argument('--json',action='store_true');p.add_argument('--video',type=pathlib.Path);a=p.parse_args()
    tools={n:shutil.which(n) for n in ('ffmpeg','ffprobe')}
    report={'tools':tools,'PIL':importlib.util.find_spec('PIL') is not None,'yaml_module':importlib.util.find_spec('yaml') is not None,
      'file_access':None,'metadata':None,'full_decode':None,'semantic_observation':'unverified','image_editor':'unverified','capability_level':'unknown'}
    if a.video:
        report['file_access']=a.video.is_file()
        if report['file_access'] and tools['ffprobe']:
            try:
                r=subprocess.run([tools['ffprobe'],'-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',str(a.video)],capture_output=True,text=True,timeout=30)
                report['metadata']=json.loads(r.stdout) if r.returncode==0 else {'error':r.stderr.strip()}
            except (subprocess.SubprocessError,ValueError) as exc:report['metadata']={'error':str(exc)}
        if report['file_access'] and tools['ffmpeg']:
            try:
                r=subprocess.run([tools['ffmpeg'],'-nostdin','-v','error','-xerror','-i',str(a.video),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,timeout=180)
                report['full_decode']={'passed':r.returncode==0,'error':r.stderr.strip()}
            except subprocess.TimeoutExpired:report['full_decode']={'passed':False,'error':'full-decode timeout; not proof of completion'}
    report['note']='Missing local ffmpeg is not automatically D: inspect alternate media tools. Metadata is not full decode; decode is not semantic observation. A/B require actual editor evidence.'
    print(json.dumps(report,ensure_ascii=False,indent=None if a.json else 2));return 0
if __name__=='__main__':raise SystemExit(main())
