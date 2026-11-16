import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from packages.music.session import run_session
from packages.music.midi import write_midi
from services.session_backup import export_session, restore_session
from test_evaluate import score

class SessionBackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root/'s.mid'; self.reference = self.root/'r.mid'
        self.source.write_bytes(write_midi(score([(p,0,1) for p in [36,48,60,67,84]])))
        self.reference.write_bytes(write_midi(score([(36,0,1),(84,0,1)])))
        self.session = self.root/'session'; self.archive = self.root/'backup.zip'
        run_session(self.source.read_bytes(),self.reference.read_bytes(),self.session,1)
        export_session(self.session,self.source,self.reference,self.archive)

    def rewrite(self, transform):
        with zipfile.ZipFile(self.archive) as z: files = {n:z.read(n) for n in z.namelist()}
        transform(files)
        with zipfile.ZipFile(self.archive,'w') as z:
            for n,data in files.items(): z.writestr(n,data)

    def test_roundtrip_and_resume_identical(self):
        dest = self.root/'restored'; restore_session(self.archive,dest)
        for p in self.session.glob('*.json'): self.assertEqual(p.read_bytes(),(dest/p.name).read_bytes())
        expected = run_session(self.source.read_bytes(),self.reference.read_bytes(),self.session,2,resume=True)
        actual = run_session((dest/'source.mid').read_bytes(),(dest/'reference.mid').read_bytes(),dest,2,resume=True)
        self.assertEqual(expected,actual)

    def test_no_overwrite(self):
        with self.assertRaises(FileExistsError): export_session(self.session,self.source,self.reference,self.archive)
        with self.assertRaises(FileExistsError): restore_session(self.archive,self.session)

    def test_tampering_and_traversal_cleanup(self):
        self.rewrite(lambda files: files.update({'source.mid':b'corrupt'}))
        with self.assertRaises(ValueError): restore_session(self.archive,self.root/'bad')
        self.assertFalse((self.root/'bad').exists())
        self.rewrite(lambda files: files.update({'../escape':b'bad'}))
        with self.assertRaises(ValueError): restore_session(self.archive,self.root/'bad')
        self.assertFalse((self.root/'escape').exists())
        self.assertEqual(list(self.root.glob('.session-restore-*')),[])

    def test_incompatible_environment_and_limits(self):
        with patch('services.session_backup.environment',return_value={}):
            with self.assertRaises(ValueError): restore_session(self.archive,self.root/'bad')
        with patch('services.session_backup.MAX_TOTAL',10):
            with self.assertRaises(ValueError): restore_session(self.archive,self.root/'bad')

    def test_wrong_inputs_and_corrupt_chain(self):
        with self.assertRaises(ValueError): export_session(self.session,self.reference,self.source,self.root/'wrong.zip')
        def corrupt(files):
            name='generation-00001.json'; payload=json.loads(files[name]); payload['payload']['previous_sha256']='bad'
            from packages.music.session import digest
            payload['sha256']=digest(payload['payload']); files[name]=json.dumps(payload).encode()
            manifest=json.loads(files['manifest.json'])
            from services.session_backup import sha
            manifest['files'][name]={'bytes':len(files[name]),'sha256':sha(files[name])}
            files['manifest.json']=json.dumps(manifest).encode()
        self.rewrite(corrupt)
        with self.assertRaises(ValueError): restore_session(self.archive,self.root/'bad')

    def test_symlink_entries(self):
        with zipfile.ZipFile(self.archive,'a') as z:
            info=zipfile.ZipInfo('generation-99999.json'); info.external_attr=0o120777<<16
            z.writestr(info,'target')
        with self.assertRaises(ValueError): restore_session(self.archive,self.root/'bad')

    def test_duplicate_entries(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(self.archive,'a') as z: z.writestr('source.mid', b'duplicate')
        with self.assertRaises(ValueError): restore_session(self.archive,self.root/'bad')
