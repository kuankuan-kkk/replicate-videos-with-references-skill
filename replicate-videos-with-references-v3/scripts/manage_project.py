#!/usr/bin/env python3
"""Versioned local state transactions with revision checks and no silent retry reset."""
import argparse,json,os,pathlib,tempfile
from project_contract import load,validate,now,file_hash,digest,constraint_hash,downgrade_scope,approval_digest,quality_passed,STATES
TRANSITIONS={'intake':['evidence-ready'],'evidence-ready':['analyzed'],'analyzed':['planned'],
 'planned':['generating','analysis-delivered'],'generating':['qa'],'qa':['storyboard-delivered'],
 'storyboard-delivered':['storyboard-approved'],'storyboard-approved':['prompts-delivered'],
 'prompts-delivered':[],'analysis-delivered':[]}
def invalidate(d):
    for r in d['approval']['records']:
        a=next((x for x in d['base_frames'] if x['id']==r.get('action_id')),None)
        if r.get('active') and (a is None or r.get('constraint_sha256')!=constraint_hash(d,a)):
            r.update(active=False,revoked_at=now(),revoked_reason='dependencies changed')
    d['approval'].pop('video_prompt_request',None)
def apply(d,args,base):
    actor=args.actor
    if not actor.strip():raise ValueError('actor required')
    a=next((x for x in d['base_frames'] if x['id']==args.action_id),None) if args.action_id else None
    if args.command=='update':
        patch=load(args.data)
        if not isinstance(patch,dict):raise ValueError('update must be object')
        allowed={'project','defaults','sources','references','request','shots','base_frames','continuity','fusion','notes'}
        if set(patch)-allowed:raise ValueError('use dedicated commands for approval, history and events')
        # A partial action update may replace its planning fields but must preserve immutable versions/repairs.
        if 'base_frames' in patch:
            existing={x['id']:x for x in d['base_frames']}
            if not isinstance(patch['base_frames'],list):raise ValueError('base_frames must be list')
            if not all(x['id'] in [y.get('id') for y in patch['base_frames']] for x in d['base_frames']):raise ValueError('cannot delete historical actions; mark omitted separately')
            for x in patch['base_frames']:
                if x.get('id') in existing:
                    for key in ['versions','repairs']:
                        if key in x and x[key]!=existing[x['id']][key]:raise ValueError('cannot overwrite version/repair history')
                        x[key]=existing[x['id']][key]
        if 'project' in patch:
            if set(patch['project'])-{'mode','route','language','capability_level','capability_evidence'}:raise ValueError('cannot directly set state/id')
            d['project'].update(patch.pop('project'))
        d.update(patch);invalidate(d);d['project']['status']='intake'
    elif args.command=='accept-downgrade':
        if d['project']['capability_level']!='B':raise ValueError('only B requires this downgrade acceptance')
        d['request']['downgrade_acceptance']={'accepted':True,'actor':actor,'at':now(),'scope_sha256':downgrade_scope(d)}
        invalidate(d);d['project']['status']='intake'
    elif args.command=='revoke-downgrade':
        d['request']['downgrade_acceptance']=None;invalidate(d);d['project']['status']='intake'
    elif args.command=='advance':
        old=d['project']['status']
        if args.state not in TRANSITIONS.get(old,[]):raise ValueError(f'illegal transition {old} -> {args.state}')
        d['project']['status']=args.state
    elif args.command=='record-version':
        if a is None:raise ValueError('unknown action')
        if d['project']['status'] not in ['generating','qa']:raise ValueError('version requires generation/QA state')
        for issue in {r['issue_id'] for r in a['repairs']}:
            history=[r for r in a['repairs'] if r['issue_id']==issue]
            epoch=sum(r['outcome']=='human-reset' for r in history)
            if sum(r['outcome']=='fail' and r.get('epoch',0)==epoch for r in history)>=2:raise ValueError('issue blocked across regeneration; record human-reviewed new plan: '+issue)
        output=pathlib.Path(args.file).resolve();vid=args.version_id
        if not vid or any(v['id']==vid for x in d['base_frames'] for v in x['versions']):raise ValueError('unique version_id required')
        if any(file_hash(base/v['output']['path'])!=v['output']['sha256'] for x in d['base_frames'] for v in x['versions']):raise ValueError('historical output replaced')
        if any((base/v['output']['path']).resolve()==output for x in d['base_frames'] for v in x['versions']):raise ValueError('output path is already an immutable version')
        version={'id':vid,'output':{'path':os.path.relpath(output,base),'sha256':file_hash(output)},'constraint_sha256':constraint_hash(d,a),'review':None,'created_by':actor,'created_at':now()}
        if args.mask:version['edit_mask']={'path':os.path.relpath(pathlib.Path(args.mask).resolve(),base),'sha256':file_hash(args.mask)}
        if args.report:version['outside_mask_report']={'path':os.path.relpath(pathlib.Path(args.report).resolve(),base),'sha256':file_hash(args.report)}
        a['versions'].append(version);a['selected_version_id']=vid
        invalidate(d)
        for r in d['approval']['records']:
            if r.get('action_id')==a['id'] and r.get('active'):r.update(active=False,revoked_at=now(),revoked_reason='new selected output version')
        d['approval'].pop('video_prompt_request',None);d['project']['status']='qa'
    elif args.command=='review':
        if a is None:raise ValueError('unknown action')
        if d['project']['status']!='qa':raise ValueError('review requires QA state')
        v=next((v for v in a['versions'] if v['id']==a['selected_version_id']),None)
        if v is None:raise ValueError('no selected version')
        v['review']={'actor':actor,'at':now(),'checks':load(args.data)}
    elif args.command=='approve':
        if d['project']['status']!='storyboard-delivered':raise ValueError('explicit approval requires delivered passing storyboard')
        ids=args.action_ids
        if not ids:raise ValueError('explicit action scope required')
        for aid in ids:
            item=next((x for x in d['base_frames'] if x['id']==aid),None)
            if not item:raise ValueError('unknown action '+aid)
            v=next((x for x in item['versions'] if x['id']==item['selected_version_id']),None)
            if not v or not quality_passed(d,item,v,base):raise ValueError('quality gate fails '+aid)
            for r in d['approval']['records']:
                if r.get('action_id')==aid and r.get('active'):r.update(active=False,revoked_at=now(),revoked_reason='superseded approval')
            d['approval']['records'].append({'action_id':aid,'version_id':v['id'],'constraint_sha256':constraint_hash(d,item),'output_sha256':v['output']['sha256'],'actor':actor,'at':now(),'active':True})
        if all(any(r.get('active') and r.get('action_id')==x['id'] and r.get('version_id')==x['selected_version_id'] for r in d['approval']['records']) for x in d['base_frames']):d['project']['status']='storyboard-approved'
    elif args.command=='authorize-video':
        if d['project']['status']!='storyboard-approved':raise ValueError('all requested actions must be explicitly approved first')
        d['approval']['video_prompt_request']={'actor':actor,'at':now(),'approval_sha256':approval_digest(d)}
        d['project']['status']='prompts-delivered'
    elif args.command=='record-repair':
        if a is None:raise ValueError('unknown action')
        if d['project']['status']!='qa':raise ValueError('repairs require QA state')
        if not args.issue_id or not args.strategy:raise ValueError('issue and distinct strategy required')
        history=[r for r in a['repairs'] if r['issue_id']==args.issue_id]
        epoch=sum(r.get('outcome')=='human-reset' for r in history)
        failures=[r for r in history if r.get('epoch',0)==epoch and r['outcome']=='fail']
        if len(failures)>=2:raise ValueError('blocked after two failures; record an explicit new human plan first')
        if any(r['strategy']==args.strategy for r in history if r.get('epoch',0)==epoch):raise ValueError('strategy already attempted for this issue')
        a['repairs'].append({'id':'repair-'+str(len(a['repairs'])+1),'issue_id':args.issue_id,'strategy':args.strategy,'actor':actor,'at':now(),'outcome':args.outcome,'epoch':epoch})
    elif args.command=='reset-repair':
        if a is None or not args.issue_id or not args.strategy:raise ValueError('action, issue and human-reviewed new plan required')
        if d['project']['status']!='qa':raise ValueError('new repair plan requires QA state')
        if any(r['issue_id']==args.issue_id and r['outcome']=='human-reset' and r['strategy']==args.strategy for r in a['repairs']):raise ValueError('human plan already used; record a materially different plan')
        a['repairs'].append({'id':'repair-'+str(len(a['repairs'])+1),'issue_id':args.issue_id,'strategy':args.strategy,'actor':actor,'at':now(),'outcome':'human-reset'})
    else:raise ValueError('unknown command')
    return d
def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['update','advance','accept-downgrade','revoke-downgrade','record-version','review','approve','authorize-video','record-repair','reset-repair'])
    parser.add_argument('manifest',type=pathlib.Path);parser.add_argument('--expected-revision',type=int,required=True);parser.add_argument('--actor',required=True)
    parser.add_argument('--data',type=pathlib.Path);parser.add_argument('--state',choices=STATES);parser.add_argument('--action-id');parser.add_argument('--action-ids',nargs='+');parser.add_argument('--file');parser.add_argument('--version-id');parser.add_argument('--mask');parser.add_argument('--report');parser.add_argument('--issue-id');parser.add_argument('--strategy');parser.add_argument('--outcome',choices=['pass','fail'])
    args=parser.parse_args();manifest=args.manifest.resolve();lock=manifest.with_suffix(manifest.suffix+'.lock');locked=False
    try:
        with lock.open('x') as f:f.write(str(os.getpid()))
        locked=True;d=load(manifest)
        if d['revision']!=args.expected_revision:raise ValueError('revision conflict; reload before editing')
        prior=validate(d,manifest.parent)
        if prior:raise ValueError('input invalid: '+'; '.join(prior))
        d=apply(d,args,manifest.parent);errors=validate(d,manifest.parent)
        if errors:raise ValueError('; '.join(errors))
        d['revision']+=1;d['events'].append({'event':args.command,'actor':args.actor,'at':now(),'revision':d['revision']})
        fd,tmp=tempfile.mkstemp(prefix=manifest.name+'.',dir=manifest.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
            os.replace(tmp,manifest)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
        print('saved revision',d['revision']);return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:print('ERROR:',exc);return 1
    finally:
        if locked:lock.unlink(missing_ok=True)
if __name__=='__main__':raise SystemExit(main())
