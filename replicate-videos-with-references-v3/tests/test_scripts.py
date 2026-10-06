import json,pathlib,re,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from project_contract import file_hash
class ScriptTests(unittest.TestCase):
    def test_init_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'project.json'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_project.py'),'Sample Project','--output',str(p)],check=True,capture_output=True)
            subprocess.run([sys.executable,str(ROOT/'scripts/validate_project.py'),str(p)],check=True,capture_output=True)
            self.assertEqual(json.loads(p.read_text())['project']['id'],'sample-project')
            second=subprocess.run([sys.executable,str(ROOT/'scripts/init_project.py'),'Other','--output',str(p)],capture_output=True)
            self.assertNotEqual(second.returncode,0)
    def test_preflight_does_not_claim_D_from_tools_only(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/preflight.py'),'--json'],check=True,capture_output=True,text=True)
        self.assertEqual(json.loads(r.stdout)['capability_level'],'unknown')
    def test_references_exist(self):
        for file in [ROOT/'SKILL.md',*ROOT.joinpath('references').glob('*.md')]:
            for target in re.findall(r'\]\(([^)]+\.md)\)',file.read_text(encoding='utf-8')):
                self.assertTrue((file.parent/target).is_file(),(file,target))
    def test_legacy_migration_preserves_but_revokes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'old.json';out=pathlib.Path(tmp)/'new.json'
            old={'schema_version':'3.0','project':{'id':'legacy'},'approval':{'storyboard_approved':True}}
            p.write_text(json.dumps(old))
            subprocess.run([sys.executable,str(ROOT/'scripts/migrate_project.py'),str(p),'--output',str(out)],check=True,capture_output=True)
            d=json.loads(out.read_text());self.assertEqual(d['project']['status'],'intake');self.assertEqual(d['approval']['records'],[]);self.assertEqual(d['legacy_snapshot'],old)
    def test_comments_not_real_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'bad.yaml'
            p.write_text('schema_version: "3.1"\nproject:\n  id: "bad"\n# defaults: sources: references: request: shots: base_frames: continuity: qa: approval:\n')
            r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_project.py'),str(p)],capture_output=True)
            self.assertNotEqual(r.returncode,0)
if __name__=='__main__':unittest.main()
