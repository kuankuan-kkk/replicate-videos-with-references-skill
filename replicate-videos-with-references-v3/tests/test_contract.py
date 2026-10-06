import copy,json,pathlib,subprocess,sys,tempfile,unittest,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from project_contract import template,validate,file_hash,now,constraint_hash,downgrade_scope,approval_digest,CHECKS,resolution_scope
from manage_project import apply
from types import SimpleNamespace
class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=pathlib.Path(self.temp.name)
        from PIL import Image
        for name in ['source.bin','frame.png','output.png']:
            if name.endswith('.bin'):(self.base/name).write_bytes(b'unit-test-source-not-a-video')
            else:Image.new('RGB',(9,16),'white').save(self.base/name)
    def tearDown(self):self.temp.cleanup()
    def fixture(self,state='qa'):
        d=template('test');d['project'].update(status=state,capability_level='B',capability_evidence={'checked_at':now(),'method':'synthetic unit fixture only','frame_extraction':True,'image_editing':True})
        d['request'].update(authorized_changes=['change product color'],cleanup_authorized=True)
        d['sources']=[{'id':'V01','path':'source.bin','sha256':file_hash(self.base/'source.bin'),'duration_seconds':4,'width':9,'height':16,'camera':'fixed','access_verified':True,'decode_verified':True,'observation_complete':True}]
        d['shots']=[{'id':'S01','source_id':'V01','start_seconds':0,'end_seconds':4}]
        d['request']['downgrade_acceptance']={'accepted':True,'actor':'user','at':now(),'scope_sha256':downgrade_scope(d)}
        a={'id':'B01','source_shot_ids':['S01'],'start':'cup on table','action':'take cup','result':'cup held','next_handoff':'held','estimated_duration_seconds':3,'camera':'fixed','aspect_ratio':'9:16','baseline':{'path':'frame.png','sha256':file_hash(self.base/'frame.png')},'state_ids':{},'depends_on':[],'versions':[],'repairs':[],'selected_version_id':'B01-v1'}
        d['base_frames']=[a];v={'id':'B01-v1','constraint_sha256':constraint_hash(d,a),'output':{'path':'output.png','sha256':file_hash(self.base/'output.png')},'review':{'actor':'reviewer','at':now(),'checks':{k:'pass' for k in CHECKS}}};a['versions']=[v]
        if state in ['storyboard-approved','prompts-delivered']:
            d['approval']['records']=[{'action_id':'B01','version_id':'B01-v1','output_sha256':v['output']['sha256'],'constraint_sha256':v['constraint_sha256'],'actor':'user','at':now(),'active':True}]
        if state=='prompts-delivered':d['approval']['video_prompt_request']={'actor':'user','at':now(),'approval_sha256':approval_digest(d)}
        return d
    def args(self,command,**values):return SimpleNamespace(command=command,actor='tester',action_id=None,data=None,state=None,action_ids=None,file=None,version_id=None,mask=None,report=None,issue_id=None,strategy=None,outcome=None,**values)
    def test_init_valid(self):self.assertEqual(validate(template('sample'),self.base),[])
    def test_real_delivery_fixture_valid(self):self.assertEqual(validate(self.fixture('prompts-delivered'),self.base),[])
    def test_wrong_types(self):
        d=template('test');d['sources']=123;self.assertTrue(validate(d,self.base))
    def test_no_evidence_delivery_rejected(self):
        d=template('test');d['project']['status']='prompts-delivered';self.assertTrue(validate(d,self.base))
    def test_source_changed(self):
        d=self.fixture();(self.base/'source.bin').write_bytes(b'changed');self.assertTrue(validate(d,self.base))
    def test_output_changed(self):
        d=self.fixture('storyboard-approved');(self.base/'output.png').write_bytes(b'changed');self.assertTrue(validate(d,self.base))
    def test_revoke_consent(self):
        d=self.fixture('prompts-delivered');d['request']['downgrade_acceptance']=None;self.assertTrue(validate(d,self.base))
    def test_changed_action_approval_stale(self):
        d=self.fixture('storyboard-approved');d['base_frames'][0]['action']='different';self.assertTrue(validate(d,self.base))
    def test_bad_shot_time(self):
        d=self.fixture();d['shots'][0]['end_seconds']=8;self.assertTrue(validate(d,self.base))
    def test_source_coverage_gap(self):
        d=self.fixture();d['shots'][0]['start_seconds']=1;self.assertTrue(validate(d,self.base))
    def test_duplicate_action_id(self):
        d=self.fixture();d['base_frames'].append(copy.deepcopy(d['base_frames'][0]));self.assertTrue(validate(d,self.base))
    def test_missing_source_mapping(self):
        d=self.fixture();d['base_frames'][0]['source_shot_ids']=['absent'];self.assertTrue(validate(d,self.base))
    def test_dependency_cycle(self):
        d=self.fixture();d['base_frames'][0]['depends_on']=['B01'];self.assertTrue(validate(d,self.base))
    def test_partial_checks(self):
        d=self.fixture('storyboard-delivered');d['base_frames'][0]['versions'][0]['review']['checks']={'light':'pass'};self.assertTrue(validate(d,self.base))
    def test_no_approval(self):
        d=self.fixture('storyboard-approved');d['approval']['records']=[];self.assertTrue(validate(d,self.base))
    def test_missing_prompt_request(self):
        d=self.fixture('prompts-delivered');d['approval'].pop('video_prompt_request');self.assertTrue(validate(d,self.base))
    def test_C_generation_blocked(self):
        d=self.fixture();d['project']['capability_level']='C';self.assertTrue(validate(d,self.base))
    def test_C_valid_plan_delivery(self):
        d=self.fixture('analysis-delivered');d['project']['capability_level']='C';d['base_frames'][0]['versions']=[];d['base_frames'][0]['selected_version_id']='';self.assertEqual(validate(d,self.base),[])
    def test_D_cannot_analyze(self):
        d=self.fixture('analyzed');d['project']['capability_level']='D';self.assertTrue(validate(d,self.base))
    def test_aspect_conflict(self):
        d=self.fixture('planned');d['sources'][0]['width']=16;d['sources'][0]['height']=9;self.assertTrue(validate(d,self.base))
    def test_camera_conflict(self):
        d=self.fixture('planned');d['sources'][0]['camera']='moving';self.assertTrue(validate(d,self.base))
    def test_duration_conflict(self):
        d=self.fixture('planned');d['base_frames'][0]['estimated_duration_seconds']=8;self.assertTrue(validate(d,self.base))
    def test_duration_explicit_resolution(self):
        d=self.fixture('planned');a=d['base_frames'][0];a['estimated_duration_seconds']=8
        d['request']['resolutions']=[{'kind':'duration','action_ids':['B01'],'choice':'extend-duration','actor':'user','at':now(),'constraint_sha256':resolution_scope(d,a)}];self.assertEqual(validate(d,self.base),[])
    def test_cleanup_must_be_authorized(self):
        d=self.fixture('planned');d['request']['cleanup_authorized']=False;self.assertTrue(validate(d,self.base))
    def test_two_repairs_survive_regeneration(self):
        d=self.fixture();a=d['base_frames'][0]
        for i in range(2):apply(d,SimpleNamespace(command='record-repair',actor='tester',action_id='B01',issue_id='grip',strategy='strategy'+str(i),outcome='fail'),self.base)
        self.assertEqual(validate(d,self.base),[])
        with self.assertRaises(ValueError):apply(d,SimpleNamespace(command='record-repair',actor='tester',action_id='B01',issue_id='grip',strategy='strategy3',outcome='fail'),self.base)
        apply(d,SimpleNamespace(command='reset-repair',actor='user',action_id='B01',issue_id='grip',strategy='new reviewed plan'),self.base)
        apply(d,SimpleNamespace(command='record-repair',actor='tester',action_id='B01',issue_id='grip',strategy='new approach',outcome='pass'),self.base)
        self.assertEqual(len(a['repairs']),4);self.assertEqual(validate(d,self.base),[])
    def test_illegal_skip(self):
        with self.assertRaises(ValueError):apply(template('x'),SimpleNamespace(command='advance',actor='user',action_id=None,state='prompts-delivered'),self.base)
    def test_duplicate_json_rejected(self):
        from project_contract import load
        p=self.base/'duplicate.json';p.write_text('{"revision":0,"revision":1}')
        with self.assertRaises(ValueError):load(p)
    def test_atomic_revision_conflict(self):
        p=self.base/'project.json';p.write_text(json.dumps(template('x')))
        r=subprocess.run([sys.executable,str(ROOT/'scripts/manage_project.py'),'advance',str(p),'--actor','user','--expected-revision','4','--state','evidence-ready'],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertEqual(json.loads(p.read_text())['revision'],0)
    def test_A_report_required(self):
        d=self.fixture('storyboard-delivered');d['project'].update(capability_level='A');d['project']['capability_evidence'].update(explicit_mask=True,outside_mask_compare=True)
        d['base_frames'][0]['versions'][0]['constraint_sha256']=constraint_hash(d,d['base_frames'][0]);self.assertTrue(validate(d,self.base))
    def test_A_valid_report_and_fake_PASS_rejected(self):
        from PIL import Image
        d=self.fixture('storyboard-delivered');d['project']['capability_level']='A';d['project']['capability_evidence'].update(explicit_mask=True,outside_mask_compare=True)
        mask=self.base/'mask.png';Image.new('L',(9,16),0).save(mask)
        mask_asset={'path':'mask.png','sha256':file_hash(mask)}
        d['request']['regions']=[{'id':'M01','action_ids':['B01'],'purpose':'product','approved_by':'user','approved_at':now(),'mask':mask_asset}]
        a=d['base_frames'][0];v=a['versions'][0];v['edit_mask']=mask_asset;v['constraint_sha256']=constraint_hash(d,a)
        command=[sys.executable,str(ROOT/'scripts/compare_outside_mask.py'),str(self.base/'frame.png'),str(self.base/'output.png'),str(mask),'--authorized-mask-sha256',file_hash(mask)]
        result=subprocess.run(command,capture_output=True,text=True,check=True)
        report=self.base/'report.json';report.write_text(result.stdout)
        v['outside_mask_report']={'path':'report.json','sha256':file_hash(report)}
        self.assertEqual(validate(d,self.base),[])
        Image.new('RGB',(9,16),'black').save(self.base/'output.png');v['output']['sha256']=file_hash(self.base/'output.png')
        forged=json.loads(result.stdout);forged['after_sha256']=v['output']['sha256'];report.write_text(json.dumps(forged));v['outside_mask_report']['sha256']=file_hash(report)
        self.assertTrue(validate(d,self.base),'must recompute pixels rather than trust a forged PASS field')
    def test_regeneration_cannot_bypass_failed_issue(self):
        d=self.fixture()
        for i in range(2):apply(d,SimpleNamespace(command='record-repair',actor='tester',action_id='B01',issue_id='grip',strategy='s'+str(i),outcome='fail'),self.base)
        with self.assertRaises(ValueError):apply(d,SimpleNamespace(command='record-version',actor='tester',action_id='B01',file=str(self.base/'output.png'),version_id='B01-v2',mask=None,report=None),self.base)
    def test_dependency_selected_version_invalidates_child(self):
        d=self.fixture('qa');child=copy.deepcopy(d['base_frames'][0]);child['id']='B02';child['depends_on']=['B01'];child['selected_version_id']='B02-v1';child['versions'][0]['id']='B02-v1';d['base_frames'].append(child)
        child['versions'][0]['constraint_sha256']=constraint_hash(d,child);old=constraint_hash(d,child)
        d['base_frames'][0]['selected_version_id']='B01-v2'
        self.assertNotEqual(old,constraint_hash(d,child))
    def test_real_cli_approval_request_and_revocation(self):
        manifest=self.base/'project.json';d=self.fixture('qa');manifest.write_text(json.dumps(d))
        def command(name,*flags,success=True):
            revision=json.loads(manifest.read_text())['revision']
            r=subprocess.run([sys.executable,str(ROOT/'scripts/manage_project.py'),name,str(manifest),'--actor','user','--expected-revision',str(revision),*flags],capture_output=True,text=True)
            self.assertEqual(r.returncode==0,success,r.stdout+r.stderr)
        command('advance','--state','storyboard-delivered')
        command('authorize-video',success=False)
        command('approve','--action-ids','B01')
        command('authorize-video')
        command('revoke-downgrade')
        final=json.loads(manifest.read_text());self.assertEqual(final['project']['status'],'intake');self.assertFalse(final['approval']['records'][0]['active']);self.assertNotIn('video_prompt_request',final['approval'])
    def test_frame_no_output_rejected(self):
        from unittest.mock import patch
        spec=importlib.util.spec_from_file_location('extract_test',ROOT/'scripts/extract_frame.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        responses=[SimpleNamespace(stdout='{"format":{"duration":"4"}}'),SimpleNamespace(returncode=0,stderr='')]
        with patch.object(sys,'argv',['extract_frame.py',str(self.base/'source.bin'),'1',str(self.base/'missing.png')]),patch.object(m.shutil,'which',return_value='mock-media-tool'),patch.object(m.subprocess,'run',side_effect=responses):
            with self.assertRaises(SystemExit) as cm:m.main()
        self.assertNotEqual(cm.exception.code,0)
class MaskTests(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        self.t=tempfile.TemporaryDirectory();self.base=pathlib.Path(self.t.name)
        self.files=[self.base/x for x in ['before.png','after.png','mask.png']]
        for im,p in zip([Image.new('RGB',(4,4),'black'),Image.new('RGB',(4,4),'white'),Image.new('L',(4,4),255)],self.files):im.save(p)
    def tearDown(self):self.t.cleanup()
    def run_compare(self,*extra):
        return subprocess.run([sys.executable,str(ROOT/'scripts/compare_outside_mask.py'),*map(str,self.files),'--authorized-mask-sha256',file_hash(self.files[2]),*extra],capture_output=True,text=True)
    def test_full_white_not_verified(self):
        r=self.run_compare();self.assertEqual(r.returncode,1);self.assertFalse(json.loads(r.stdout)['pass']);self.assertEqual(json.loads(r.stdout)['status'],'not-applicable')
    def test_out_of_range_ratio(self):self.assertNotEqual(self.run_compare('--max-changed-ratio','2').returncode,0)
    def test_nonfinite_ratio(self):self.assertNotEqual(self.run_compare('--max-changed-ratio','nan').returncode,0)
    def test_modified_mask_hash_rejected(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/compare_outside_mask.py'),*map(str,self.files),'--authorized-mask-sha256','0'*64],capture_output=True,text=True);self.assertNotEqual(r.returncode,0)
    def test_valid_local_edit(self):
        from PIL import Image
        before=Image.open(self.files[0]);after=before.copy();after.putpixel((1,1),(255,255,255));after.save(self.files[1]);mask=Image.new('L',(4,4),0);mask.putpixel((1,1),255);mask.save(self.files[2])
        r=self.run_compare();self.assertEqual(r.returncode,0);self.assertEqual(json.loads(r.stdout)['locked_pixels'],15)
    def test_non_binary_mask_rejected(self):
        from PIL import Image
        Image.new('L',(4,4),127).save(self.files[2]);self.assertNotEqual(self.run_compare().returncode,0)
if __name__=='__main__':unittest.main()
