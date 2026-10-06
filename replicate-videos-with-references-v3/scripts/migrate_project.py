#!/usr/bin/env python3
"""Preserve v3.0 as an audit snapshot; never carry legacy approval into v3.1."""
import argparse,json,pathlib
from project_contract import load,template,now,file_hash
def main():
    p=argparse.ArgumentParser();p.add_argument('legacy',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
    old=load(a.legacy)
    if not isinstance(old,dict) or str(old.get('schema_version'))!='3.0':p.error('expected legacy v3.0')
    ident=old.get('project',{}).get('id')
    if not isinstance(ident,str) or not ident.strip():p.error('legacy project id missing')
    d=template(ident);d['legacy_snapshot']=old
    d['notes'].append('Legacy drafts preserved in legacy_snapshot. Re-register verified files, action schema and versions; approval resets to intake.')
    d['events'].append({'event':'legacy-imported','at':now(),'legacy_sha256':file_hash(a.legacy)})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
    print(a.output.resolve());return 0
if __name__=='__main__':raise SystemExit(main())
