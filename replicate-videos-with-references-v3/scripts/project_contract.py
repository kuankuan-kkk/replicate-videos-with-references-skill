"""v3.1 structured contract. Canonical JSON; YAML requires PyYAML.
Local validation is not a tamper-proof production authorization service.
"""
import hashlib,json,math,pathlib,datetime
STATES=['intake','evidence-ready','analyzed','planned','generating','qa','storyboard-delivered','storyboard-approved','prompts-delivered','analysis-delivered']
MODES=['strict-local-redraw','multi-video-fusion','scene-transplant']
CHECKS=['boundary','action','identity','anatomy','space','wardrobe','product','light','format']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def file_hash(p):
    h=hashlib.sha256()
    with pathlib.Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def load(p):
    text=pathlib.Path(p).read_text(encoding='utf-8-sig')
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('duplicate key: '+k)
            out[k]=v
        return out
    try:return json.loads(text,object_pairs_hook=pairs)
    except json.JSONDecodeError:
        try:import yaml
        except ImportError as exc:raise ValueError('Ordinary YAML needs PyYAML; use canonical JSON from init_project.py. No regex fallback.') from exc
        class Unique(yaml.SafeLoader):pass
        def mapping(loader,node,deep=False):return pairs([(loader.construct_object(k,deep=deep),loader.construct_object(v,deep=deep)) for k,v in node.value])
        Unique.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
        return yaml.load(text,Loader=Unique)
def template(project_id):
    return {'schema_version':'3.1','revision':0,'project':{'id':project_id,'mode':'strict-local-redraw','route':'storyboard','status':'intake','language':'zh-CN','capability_level':'unknown','capability_evidence':{}},
    'defaults':{'aspect_ratio':'9:16','duration_seconds':4,'video_camera':'fixed','remove_subtitles':True,'remove_usernames':True,'remove_platform_ui':True,'remove_watermarks':True},
    'sources':[],'references':{'characters':[],'products':[],'scenes':[]},
    'request':{'authorized_changes':[],'explicit_locks':[],'requested_count':None,'count_semantics':'natural','regions':[],'resolutions':[],'downgrade_acceptance':None,'cleanup_authorized':False},
    'shots':[],'base_frames':[],'continuity':{'outfits':[],'rooms':[],'products':[],'objects':[]},'fusion':{'contributions':[]},'qa':{'failures':[]},'approval':{'records':[]},'notes':[],'events':[]}
def constraint_hash(d,a=None):
    scope={k:a.get(k) for k in ['id','source_shot_ids','start','action','result','next_handoff','estimated_duration_seconds','camera','aspect_ratio','baseline','state_ids','depends_on']} if a else None
    deps={x['id']:{**{k:x.get(k) for k in ['start','action','result','next_handoff','state_ids']},'selected_version_id':x.get('selected_version_id'),'selected_output_sha256':next((v.get('output',{}).get('sha256') for v in x.get('versions',[]) if v.get('id')==x.get('selected_version_id')),None)} for x in d['base_frames'] if a and x['id'] in a.get('depends_on',[])}
    return digest({'project':{k:d['project'].get(k) for k in ['mode','route','capability_level','capability_evidence']},'request':d['request'],'defaults':d['defaults'],'sources':d['sources'],'references':d['references'],'continuity':d['continuity'],'action':scope,'upstream':deps})
def resolution_scope(d,a):
    c=json.loads(json.dumps(d));c['request']['resolutions']=[];return constraint_hash(c,a)
def downgrade_scope(d):return digest({'capability':d['project']['capability_level'],'evidence':d['project']['capability_evidence'],'sources':[(s.get('id'),s.get('sha256')) for s in d['sources']]})
def approval_digest(d):return digest([r for r in d['approval']['records'] if r.get('active') is True])
def quality_passed(d,a,v,base,verify_files=True):
    try:
        r=v['review']
        if v['constraint_sha256']!=constraint_hash(d,a) or not r['actor'].strip() or not r['at'].strip():return False
        if set(r['checks'])!=set(CHECKS) or any(x not in ['pass','not-applicable'] for x in r['checks'].values()):return False
        if any(r['checks'][x]!='pass' for x in ['boundary','action','format']):return False
        if d['project']['capability_level']=='A':
            asset=v['outside_mask_report'];p=pathlib.Path(base)/asset['path']
            if verify_files and file_hash(p)!=asset['sha256']:return False
            report=json.loads(p.read_text(encoding='utf-8'))
            masks=[x['mask']['sha256'] for x in d['request']['regions'] if a['id'] in x.get('action_ids',[]) and 'mask' in x]
            if not masks or v['edit_mask']['sha256'] not in masks:return False
            if report['status']!='verified' or report['pass'] is not True or report['locked_pixels']<=0:return False
            if report['before_sha256']!=a['baseline']['sha256'] or report['after_sha256']!=v['output']['sha256']:return False
            if report['mask_sha256']!=v['edit_mask']['sha256'] or report['authorized_mask_sha256']!=v['edit_mask']['sha256']:return False
            if report['channel_tolerance']!=2 or report['max_changed_ratio']!=.001:return False
            if verify_files:
                # A handwritten PASS report is not evidence: recompute from the registered files.
                from PIL import Image,ImageChops
                with Image.open(pathlib.Path(base)/a['baseline']['path']) as src,Image.open(pathlib.Path(base)/v['output']['path']) as out,Image.open(pathlib.Path(base)/v['edit_mask']['path']) as mask:
                    if src.size!=out.size or src.size!=mask.size:return False
                    m=mask.convert('L')
                    hist=m.histogram()
                    if sum(hist[1:255]) or hist[0]<=0:return False
                    locked=m.point(lambda n:255 if n==0 else 0)
                    diff=ImageChops.difference(src.convert('RGB'),out.convert('RGB'))
                    channels=[band.point(lambda n:255 if n>2 else 0) for band in diff.split()]
                    changed=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2])
                    changed_count=ImageChops.multiply(changed,locked).histogram()[255]
                    if changed_count/hist[0]>.001:return False
                    if report['locked_pixels']!=hist[0] or report['changed_locked_pixels']!=changed_count:return False
                    if not isinstance(report.get('changed_ratio'),(float,int)) or abs(report['changed_ratio']-changed_count/hist[0])>1e-12:return False
        return True
    except (KeyError,TypeError,ValueError,OSError,AttributeError,ImportError):return False
def validate(d,base,verify_files=True):
    errors=[];base=pathlib.Path(base)
    def check(c,m):
        if not c:errors.append(m)
    def named(v):return isinstance(v,str) and bool(v.strip())
    def num(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
    def fields(o,types,label):
        if not isinstance(o,dict):errors.append(label+': expected object');return False
        good=True
        for k,t in types.items():
            if k not in o or type(o[k]) is not t:errors.append(f'{label}.{k}: expected {t.__name__}');good=False
        return good
    def asset(o,label):
        if not fields(o,{'path':str,'sha256':str},label):return
        check(named(o['path']),label+': empty path');check(len(o['sha256'])==64 and all(c in '0123456789abcdef' for c in o['sha256']),label+': invalid hash')
        if verify_files:
            try:check((base/o['path']).is_file() and file_hash(base/o['path'])==o['sha256'],label+': missing/changed file')
            except OSError as exc:errors.append(label+': '+str(exc))
    def unique(items,label):
        found={}
        for x in items:
            if not isinstance(x,dict) or not named(x.get('id')):errors.append(label+': missing ID');continue
            check(x['id'] not in found,label+': duplicate ID');found[x['id']]=x
        return found
    if not fields(d,{'schema_version':str,'revision':int,'project':dict,'defaults':dict,'sources':list,'references':dict,'request':dict,'shots':list,'base_frames':list,'continuity':dict,'fusion':dict,'qa':dict,'approval':dict,'notes':list,'events':list},'manifest'):return errors
    check(d['schema_version']=='3.1','schema_version must be 3.1; legacy must migrate');check(d['revision']>=0,'invalid revision')
    p=d['project'];req=d['request'];defs=d['defaults']
    if not fields(p,{'id':str,'mode':str,'route':str,'status':str,'capability_level':str,'capability_evidence':dict},'project'):return errors
    check(named(p['id']),'empty project.id');check(p['mode'] in MODES,'invalid mode');check(p['route'] in ['analysis','image-prompts','storyboard','video-prompts','end-to-end'],'invalid route');check(p['status'] in STATES,'invalid state');check(p['capability_level'] in ['unknown','A','B','C','D'],'invalid capability')
    if not fields(req,{'authorized_changes':list,'explicit_locks':list,'regions':list,'resolutions':list,'count_semantics':str,'cleanup_authorized':bool},'request'):return errors
    if not fields(d['references'],{'characters':list,'products':list,'scenes':list},'references') or not fields(d['continuity'],{'outfits':list,'rooms':list,'products':list,'objects':list},'continuity'):return errors
    if not fields(d['approval'],{'records':list},'approval') or not fields(d['qa'],{'failures':list},'qa') or not fields(d['fusion'],{'contributions':list},'fusion'):return errors
    check('downgrade_acceptance' in req,'missing downgrade_acceptance');check(req['count_semantics'] in ['natural','maximum','exact','test-batch','additions'],'invalid count semantics')
    count=req.get('requested_count')
    if req['count_semantics']!='natural':check(type(count) is int and count>0,'count must be positive integer')
    check(named(defs.get('aspect_ratio')) and named(defs.get('video_camera')) and num(defs.get('duration_seconds')) and defs.get('duration_seconds',0)>0,'invalid defaults')
    sources=unique(d['sources'],'sources');shots=unique(d['shots'],'shots');actions=unique(d['base_frames'],'actions');regions=unique(req['regions'],'regions');versions={}
    for key,items in d['references'].items():
        if isinstance(items,list):
            unique(items,'references.'+key)
            for x in items:asset(x,'reference')
    for s in sources.values():
        asset(s,'source '+s['id']);check(num(s.get('duration_seconds')) and s.get('duration_seconds',0)>0,'invalid source duration')
        check(type(s.get('width')) is int and s['width']>0 and type(s.get('height')) is int and s['height']>0,'invalid source dimensions')
        for k in ['access_verified','decode_verified','observation_complete']:check(type(s.get(k)) is bool,'source '+k+' must be bool')
        check(s.get('camera') in ['fixed','moving','unknown'],'source camera must be known category')
    for s in shots.values():
        check(s.get('source_id') in sources,'unknown shot source');start,end=s.get('start_seconds'),s.get('end_seconds')
        check(num(start) and num(end) and 0<=start<end,'invalid shot times')
        if s.get('source_id') in sources and num(end) and num(sources[s['source_id']].get('duration_seconds')):check(end<=sources[s['source_id']]['duration_seconds']+.001,'shot beyond duration')
    for r in regions.values():
        check(isinstance(r.get('action_ids'),list) and bool(r.get('action_ids')),'region needs action IDs')
        check(named(r.get('purpose')) and named(r.get('approved_by')) and named(r.get('approved_at')),'region needs purpose/user approval')
        if isinstance(r.get('action_ids'),list):check(all(x in actions for x in r['action_ids']),'region references missing action')
        if 'mask' in r:asset(r['mask'],'approved mask')
    active=set();seen=set()
    def visit(aid):
        if aid in active:errors.append('cyclic action dependency');return
        if aid in seen:return
        active.add(aid)
        deps=actions[aid].get('depends_on',[])
        if isinstance(deps,list):
            for x in deps:
                check(x in actions,'unknown dependency')
                if x in actions:visit(x)
        active.remove(aid);seen.add(aid)
    for aid in actions:visit(aid)
    for a in actions.values():
        if not fields(a,{'source_shot_ids':list,'start':str,'action':str,'result':str,'next_handoff':str,'camera':str,'aspect_ratio':str,'baseline':dict,'state_ids':dict,'depends_on':list,'versions':list,'repairs':list,'selected_version_id':str},'action '+a['id']):continue
        check(all(named(a[k]) for k in ['start','action','result']),'missing complete action description');check(num(a.get('estimated_duration_seconds')) and a.get('estimated_duration_seconds',0)>0,'invalid action duration')
        check(bool(a['source_shot_ids']) and all(x in shots for x in a['source_shot_ids']),'invalid action source mapping');asset(a['baseline'],'original baseline')
        for group,ids in a['state_ids'].items():
            check(group in d['continuity'] and isinstance(ids,list),'invalid continuity mapping')
            if group in d['continuity'] and isinstance(ids,list):check(all(x in {v.get('id') for v in d['continuity'][group] if isinstance(v,dict)} for x in ids),'unknown continuity ID')
        av=unique(a['versions'],'versions')
        for vid,v in av.items():
            check(vid not in versions,'duplicate global version ID');versions[vid]=(a,v)
            check(named(v.get('constraint_sha256')),'version needs constraint fingerprint');asset(v.get('output'),'version output')
            if 'edit_mask' in v:asset(v['edit_mask'],'version mask')
            if 'outside_mask_report' in v:asset(v['outside_mask_report'],'QA report')
            if v.get('review') is not None and fields(v['review'],{'actor':str,'at':str,'checks':dict},'review'):
                check(named(v['review']['actor']) and named(v['review']['at']),'review actor/time missing');check(set(v['review']['checks'])==set(CHECKS),'review dimensions incomplete')
                check(all(x in ['pass','fail','not-applicable'] for x in v['review']['checks'].values()),'invalid review values')
        check(not a['selected_version_id'] or a['selected_version_id'] in av,'selected version missing')
        for r in a['repairs']:
            check(isinstance(r,dict) and all(named(r.get(k)) for k in ['id','issue_id','strategy','at','actor']) and r.get('outcome') in ['pass','fail','human-reset'],'invalid repair history')
    state=p['status'];rank=STATES.index(state) if state in STATES and state!='analysis-delivered' else 3
    if state!='intake':
        check(p['capability_level'] in ['A','B','C'],'requires usable capability');check(bool(sources),'sources empty');check(bool(req['authorized_changes']) or p['route']=='analysis','missing authorized brief')
        for s in sources.values():check(s.get('access_verified') is True and s.get('decode_verified') is True,'source access/decode unverified')
        e=p['capability_evidence'];check(named(e.get('checked_at')) and named(e.get('method')) and e.get('frame_extraction') is True,'capability evidence incomplete')
        if p['capability_level'] in ['A','B']:check(e.get('image_editing') is True,'image editor unverified')
        if p['capability_level']=='A':check(e.get('explicit_mask') is True and e.get('outside_mask_compare') is True,'A capabilities unverified')
    if rank>=2 and state!='intake':
        check(bool(shots),'shots empty')
        for sid,s in sources.items():
            check(s.get('observation_complete') is True,'complete semantic observation unverified');cursor=0
            spans=sorted([(x['start_seconds'],x['end_seconds']) for x in shots.values() if x.get('source_id')==sid and num(x.get('start_seconds')) and num(x.get('end_seconds'))])
            for start,end in spans:check(start<=cursor+.001,'source coverage gap');cursor=max(cursor,end)
            if num(s.get('duration_seconds')):check(cursor>=s['duration_seconds']-.001,'source coverage incomplete')
    if rank>=3 and state not in ['intake','evidence-ready','analyzed']:
        check(bool(actions),'actions empty')
        if req['count_semantics'] in ['exact','test-batch']:check(len(actions)==count,'exact/test batch count mismatch')
        if req['count_semantics']=='maximum' and type(count) is int:check(len(actions)<=count,'maximum count exceeded')
        def resolved(kind,a,choices):
            return any(isinstance(r,dict) and r.get('kind')==kind and a['id'] in r.get('action_ids',[]) and r.get('choice') in choices and r.get('constraint_sha256')==resolution_scope(d,a) and named(r.get('actor')) and named(r.get('at')) for r in req['resolutions'])
        for a in actions.values():
            if not isinstance(a.get('source_shot_ids'),list):continue
            linked=[sources[shots[x]['source_id']] for x in a['source_shot_ids'] if x in shots and shots[x].get('source_id') in sources]
            if p['mode']=='strict-local-redraw' and a.get('camera')=='fixed' and any(s.get('camera')!='fixed' for s in linked):check(resolved('camera',a,['adapt-fixed']),'camera conflict: obtain explicit adaptation approval')
            if a.get('aspect_ratio')=='9:16' and any(s.get('width',0)*16!=s.get('height',0)*9 for s in linked):check(resolved('aspect',a,['letterbox','authorized-crop','authorized-expand']),'aspect conflict: preserve, letterbox or approve crop/expand')
            if num(a.get('estimated_duration_seconds')) and num(defs.get('duration_seconds')) and a['estimated_duration_seconds']>defs['duration_seconds']:check(resolved('duration',a,['extend-duration']),'duration conflict: split complete action or approve longer duration')
        if any(defs.get(k) for k in ['remove_subtitles','remove_usernames','remove_platform_ui','remove_watermarks']):check(req['cleanup_authorized'] is True,'cleanup must be explicitly authorized')
        if p['mode']=='multi-video-fusion':
            for sid in sources:check(any(isinstance(c,dict) and c.get('source_id')==sid and named(c.get('description')) and isinstance(c.get('action_ids'),list) and c['action_ids'] and all(aid in actions and any(sh in shots and shots[sh].get('source_id')==sid for sh in actions[aid].get('source_shot_ids',[])) for aid in c['action_ids']) for c in d['fusion']['contributions']),'fusion contribution missing '+sid)
    if rank>=4 and state!='analysis-delivered':
        check(p['capability_level'] in ['A','B'],'C/D cannot generate storyboard or approved-image video prompts')
        if p['capability_level']=='B':
            consent=req.get('downgrade_acceptance');check(isinstance(consent,dict) and consent.get('accepted') is True and named(consent.get('actor')) and named(consent.get('at')) and consent.get('scope_sha256')==downgrade_scope(d),'B consent absent or stale')
    for r in d['approval']['records']:
        if not isinstance(r,dict):errors.append('invalid approval');continue
        check(type(r.get('active')) is bool,'approval active must be bool')
        check(r.get('action_id') in actions and r.get('version_id') in versions,'approval action/version absent')
        if r.get('active') is True and r.get('version_id') in versions:
            a,v=versions[r['version_id']];check(a['id']==r.get('action_id'),'approval version mismatch')
            check(named(r.get('actor')) and named(r.get('at')),'approval actor/time missing')
            check(r.get('constraint_sha256')==constraint_hash(d,a)==v.get('constraint_sha256'),'approval stale constraints')
            check(r.get('output_sha256')==v.get('output',{}).get('sha256'),'approval stale image');check(quality_passed(d,a,v,base,verify_files),'approved QA invalid')
    if state in ['storyboard-delivered','storyboard-approved','prompts-delivered']:
        for a in actions.values():
            pair=versions.get(a.get('selected_version_id'));check(pair is not None and pair[0]['id']==a['id'] and quality_passed(d,a,pair[1],base,verify_files),'no passing selected version '+a['id'])
            if state in ['storyboard-approved','prompts-delivered']:check(any(isinstance(r,dict) and r.get('active') is True and r.get('action_id')==a['id'] and r.get('version_id')==a.get('selected_version_id') for r in d['approval']['records']),'missing current explicit approval '+a['id'])
        if state=='prompts-delivered':
            auth=d['approval'].get('video_prompt_request');check(isinstance(auth,dict) and named(auth.get('actor')) and named(auth.get('at')) and auth.get('approval_sha256')==approval_digest(d),'explicit video-prompt request missing/stale')
    if state=='analysis-delivered':check(p['route'] in ['analysis','image-prompts'] or p['capability_level']=='C','invalid analysis delivery route')
    return errors
