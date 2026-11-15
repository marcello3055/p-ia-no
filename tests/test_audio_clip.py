import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import wave
from packages.music.audio_clip import prepare_clip

class AudioClipTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.source=self.root/'input.mp3'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:duration=3','-c:a','libmp3lame',str(self.source)],check=True)
    def tearDown(self): self.temp.cleanup()
    def test_real_mp3_clip_cache_and_source_unchanged(self):
        before=self.source.read_bytes(); dest=self.root/'clip'
        report=prepare_clip(self.source,dest,.5,1)
        self.assertFalse(report['cache_hit']); self.assertFalse(report['silent'])
        self.assertAlmostEqual(report['actual_seconds'],1,places=3)
        self.assertEqual(report['cache_key']['source_sha256'],hashlib.sha256(before).hexdigest())
        with wave.open(str(dest/'clip.wav')) as w:
            self.assertEqual((w.getnchannels(),w.getframerate(),w.getsampwidth()),(1,22050,2))
        stamp=(dest/'clip.wav').stat().st_mtime_ns
        self.assertTrue(prepare_clip(self.source,dest,.5,1)['cache_hit'])
        self.assertEqual((dest/'clip.wav').stat().st_mtime_ns,stamp)
        self.assertEqual(self.source.read_bytes(),before)
    def test_tail_and_silence(self):
        r=prepare_clip(self.source,self.root/'tail',2,2)
        self.assertTrue(r['clipped_at_end']); self.assertAlmostEqual(r['actual_seconds'],1,delta=.05)
        silent=self.root/'silent.wav'
        with wave.open(str(silent),'wb') as w:
            w.setparams((1,2,22050,0,'NONE','not compressed')); w.writeframes(b'\0'*44100)
        self.assertTrue(prepare_clip(silent,self.root/'silence',0,1)['silent'])
    def test_invalid_limits_and_content(self):
        for start,length in [(float('nan'),1),(0,float('inf')),(-1,2),(0,31),(4,1)]:
            with self.assertRaises(ValueError): prepare_clip(self.source,self.root/'out',start,length)
        bad=self.root/'fake.mp3'; bad.write_text('not audio')
        with self.assertRaises(ValueError): prepare_clip(bad,self.root/'out')
        self.assertFalse((self.root/'out').exists())
    def test_changed_config_or_corrupt_cache_not_overwritten(self):
        dest=self.root/'out'; prepare_clip(self.source,dest,0,1)
        with self.assertRaises(ValueError): prepare_clip(self.source,dest,1,1)
        (dest/'clip.wav').write_bytes(b'corrupt')
        with self.assertRaises(ValueError): prepare_clip(self.source,dest,0,1)
        self.assertEqual((dest/'clip.wav').read_bytes(),b'corrupt')
    def test_wav_flac_and_cli(self):
        import sys
        for extension in ['wav','flac']:
            path=self.root/f'input.{extension}'
            subprocess.run(['ffmpeg','-v','error','-i',str(self.source),str(path)],check=True)
            self.assertGreater(prepare_clip(path,self.root/extension,0,1)['peak_pcm16'],0)
        p=subprocess.run([sys.executable,'scripts/prepare_audio_clip.py',str(self.source),'--output-dir',str(self.root/'cli'),'--seconds','1'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['actual_seconds'],1)
