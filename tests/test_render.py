import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import wave
from packages.music.midi import write_midi
from packages.music.reduce import reduce_to_piano
from packages.music.render import render_piano
from test_evaluate import score

class RenderTests(unittest.TestCase):
    def fixture(self,root,values):
        reduced,_=reduce_to_piano(score(values))
        path=root/'source.mid'; path.write_bytes(write_midi(reduced)); return path

    def test_real_wav_mp3_timing_signal_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            source=self.fixture(root,[(48,0,2),(60,1,1),(64,2,1),(67,3,1)])
            dest=root/'render'
            r=render_piano(source,dest)
            self.assertEqual(r['duration_seconds'],5)
            self.assertGreater(r['peak_pcm16'],100)
            self.assertLess(r['peak_pcm16'],32767)
            with wave.open(str(dest/'piano.wav')) as audio:
                self.assertEqual((audio.getnchannels(),audio.getframerate(),audio.getnframes()),(2,44100,220500))
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(dest/'piano.mp3')]))['streams'][0]
            self.assertEqual(probe['codec_name'],'mp3')
            self.assertAlmostEqual(float(probe['duration']),5,delta=.15)
            subprocess.run(['ffmpeg','-v','error','-i',str(dest/'piano.mp3'),'-f','null','-'],check=True,capture_output=True)
            self.assertEqual(json.loads((dest/'render.json').read_text())['program'],0)
            with self.assertRaises(ValueError):
                render_piano(source,dest)

    def test_missing_soundfont_and_long_input_leave_no_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=self.fixture(root,[(60,0,1)])
            with self.assertRaises(ValueError):
                render_piano(source,root/'out',root/'missing.sf2')
            source=self.fixture(root,[(60,0,250)])
            with self.assertRaises(ValueError):
                render_piano(source,root/'out')
            self.assertFalse((root/'out').exists())

    def test_reject_orchestral_program(self):
        from packages.music.midi import Event
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); s=score([(60,0,1)])
            s.events.append(Event(0,0,0,False,{'type':'program_change','program':48,'channel':0}))
            source=root/'orchestra.mid'; source.write_bytes(write_midi(s))
            with self.assertRaises(ValueError):
                render_piano(source,root/'out')
            self.assertFalse((root/'out').exists())
