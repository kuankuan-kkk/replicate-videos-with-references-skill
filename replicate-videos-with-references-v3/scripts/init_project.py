#!/usr/bin/env python3
"""Create canonical JSON (valid YAML too), without external dependencies."""
import argparse,json,pathlib,re
from project_contract import template,now
def main():
    p=argparse.ArgumentParser();p.add_argument('project_id');p.add_argument('--output',type=pathlib.Path,default=pathlib.Path('project.json'));a=p.parse_args()
    ident=re.sub(r'[^a-zA-Z0-9_-]+','-',a.project_id.strip()).strip('-').lower()
    if not ident:p.error('project_id needs ASCII letter/digit')
    d=template(ident);d['events'].append({'event':'created','at':now()})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
    print(a.output.resolve());return 0
if __name__=='__main__':raise SystemExit(main())
