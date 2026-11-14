import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from fastapi.testclient import TestClient
from services.api.backup import export_backup, restore_backup
from services.api.storage import Store
from services.api.main import create_app
from test_storage import wav_bytes

class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        with TestClient(create_app(self.source)) as client:
            def upload(value):
                response = client.post('/api/audio?filename=test.wav', content=wav_bytes(value), headers={'Content-Type': 'application/octet-stream'})
                self.assertEqual(response.status_code, 200)
                return response.json()['id']
            self.a, self.b = upload(0), upload(10)
            client.post('/api/pairs', json={'name': 'Pair', 'base_id': self.a, 'reference_id': self.b})
        self.archive = self.root / 'backup.zip'
        export_backup(Store(self.source), self.archive)

    def rewrite(self, transform):
        with zipfile.ZipFile(self.archive) as z:
            entries = {name: z.read(name) for name in z.namelist()}
        transform(entries)
        target = self.root / 'modified.zip'
        with zipfile.ZipFile(target, 'w') as z:
            for name, data in entries.items():
                z.writestr(name, data)
        return target

    def test_restore_into_new_directory_preserves_ids_pairs_and_bytes(self):
        target = self.root / 'restored'
        self.assertEqual(restore_backup(self.archive, target), {'audio_count': 2, 'pair_count': 1})
        with TestClient(create_app(target)) as client:
            self.assertEqual(client.get('/api/audio/' + self.a + '/content').content, wav_bytes(0))
            self.assertEqual(client.get('/api/audio/' + self.b + '/content').content, wav_bytes(10))
            self.assertEqual(client.get('/api/pairs').json()[0]['name'], 'Pair')

    def test_existing_destination_and_archive_never_overwritten(self):
        original = self.archive.read_bytes()
        with self.assertRaises(FileExistsError):
            export_backup(Store(self.source), self.archive)
        with self.assertRaises(FileExistsError):
            restore_backup(self.archive, self.source)
        self.assertEqual(original, self.archive.read_bytes())
        self.assertEqual(len(Store(self.source).get_audio(self.a)['id']), 32)

    def test_corruption_rolls_back_new_directory(self):
        def change(entries):
            key = next(k for k in entries if k.startswith('audio/'))
            entries[key] = entries[key][:-1] + b'x'
        target = self.root / 'restored'
        with self.assertRaises(ValueError):
            restore_backup(self.rewrite(change), target)
        self.assertFalse(target.exists())

    def test_traversal_extra_file_rejected_without_extracting(self):
        target = self.root / 'restored'
        with self.assertRaises(ValueError):
            restore_backup(self.rewrite(lambda e: e.update({'../escape.txt': b'bad'})), target)
        self.assertFalse(target.exists())
        self.assertFalse((self.root / 'escape.txt').exists())

    def test_missing_audio_and_invalid_pair_rejected(self):
        def change(entries):
            manifest = json.loads(entries['manifest.json'])
            manifest['pairs'][0]['base_id'] = '0' * 32
            entries['manifest.json'] = json.dumps(manifest).encode()
        with self.assertRaises(ValueError):
            restore_backup(self.rewrite(change), self.root / 'restored')
        def remove(entries):
            del entries[next(k for k in entries if k.startswith('audio/'))]
        with self.assertRaises(ValueError):
            restore_backup(self.rewrite(remove), self.root / 'restored')

    def test_duplicate_zip_entry_rejected(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(self.archive, 'a') as z:
                z.writestr('manifest.json', '{}')
        with self.assertRaises(ValueError):
            restore_backup(self.archive, self.root / 'restored')

    def test_symlink_and_oversized_declaration_rejected(self):
        import stat
        with zipfile.ZipFile(self.archive, 'a') as z:
            entry = zipfile.ZipInfo('symlink')
            entry.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(entry, '/etc/passwd')
        with self.assertRaises(ValueError):
            restore_backup(self.archive, self.root / 'restored')
        def change(entries):
            entries.pop('symlink')
            m = json.loads(entries['manifest.json'])
            m['audio'][0]['size'] = 2**40
            entries['manifest.json'] = json.dumps(m).encode()
        with self.assertRaises(ValueError):
            restore_backup(self.rewrite(change), self.root / 'restored')

    def test_export_missing_source_leaves_no_partial_backup(self):
        next((self.source / 'audio').glob('*.wav')).unlink()
        target = self.root / 'failed.zip'
        with self.assertRaises(FileNotFoundError):
            export_backup(Store(self.source), target)
        self.assertFalse(target.exists())
        self.assertEqual(list(self.root.glob('.piano-backup-*')), [])

    def test_download_endpoint_is_restorable(self):
        with TestClient(create_app(self.source)) as client:
            response = client.get('/api/backup')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response.headers['content-disposition'])
        downloaded = self.root / 'downloaded.zip'
        downloaded.write_bytes(response.content)
        self.assertEqual(restore_backup(downloaded, self.root / 'download-restored')['pair_count'], 1)

    def test_empty_library_backup_is_valid(self):
        empty = Store(self.root / 'empty')
        path = self.root / 'empty.zip'
        export_backup(empty, path)
        self.assertEqual(restore_backup(path, self.root / 'empty-restored'), {'audio_count': 0, 'pair_count': 0})
