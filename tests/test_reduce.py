import copy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from packages.music.midi import Event, read_midi, write_midi
from packages.music.reduce import ReductionConfig, reduce_to_piano
from test_evaluate import score

class ReductionTests(unittest.TestCase):
    def test_extremes_density_and_roundtrip(self):
        source=score([(p,0,1) for p in [36,40,43,47,60,64,67,72]])
        out,report=reduce_to_piano(source)
        self.assertEqual({n.pitch for n in out.notes},{36,40,43,72,67,64})
        self.assertEqual(report['discard_counts'],{'hand_polyphony':2})
        restored=read_midi(write_midi(out))
        self.assertEqual(len(restored.notes),6)
        self.assertEqual({n.channel for n in restored.notes},{0})
        self.assertEqual({n.track for n in restored.notes},{1,2})

    def test_sustained_span_and_capacity(self):
        out,r=reduce_to_piano(score([(72,0,4),(60,1,2),(59,1,2),(84,2,1),(67,2,1),(65,2,1)]),ReductionConfig(max_notes_per_hand=2))
        self.assertEqual({n.pitch for n in out.notes},{72,60,59})
        self.assertEqual(r['discard_counts'],{'hand_polyphony':3})
        _,r=reduce_to_piano(score([(72,0,4),(85,1,1)]))
        self.assertEqual(r['discard_counts'],{'hand_span':1})

    def test_duplicate_and_boundary_reattack(self):
        out,r=reduce_to_piano(score([(60,0,1),(60,0,2),(60,.5,1),(60,1,1)]))
        self.assertEqual(r['discard_counts'],{'overlapping_same_pitch':2})
        self.assertEqual(len(read_midi(write_midi(out)).notes),2)

    def test_filter_range_drums_zero_and_instruments(self):
        source=score([(20,0,1),(109,0,1),(64,0,0),(36,0,1),(72,0,1)])
        source.notes[3]=replace(source.notes[3],channel=9)
        source.events += [Event(0,0,4,False,{'type':'program_change','channel':0,'program':48}),Event(0,0,5,False,{'type':'control_change','channel':0,'control':64,'value':127})]
        out,r=reduce_to_piano(source)
        self.assertEqual([n.pitch for n in out.notes],[72])
        self.assertEqual(sum(r['discard_counts'].values()),4)
        self.assertEqual([e.message for e in out.events if not e.meta],[{'type':'program_change','channel':0,'program':0}])

    def test_timing_metadata_immutable_deterministic(self):
        source=score([(48,0,1),(72,1,2)],tempo=700000)
        source.events.append(Event(0,500,9,True,{'type':'set_tempo','tempo':900000}))
        original=copy.deepcopy(source)
        out,r=reduce_to_piano(source)
        self.assertEqual(source,original)
        self.assertEqual((out,r),reduce_to_piano(source))
        self.assertEqual(out.tempo_map(),source.tempo_map())
        self.assertEqual([(n.pitch,n.start_tick,n.end_tick,n.velocity) for n in out.notes],[(n.pitch,n.start_tick,n.end_tick,n.velocity) for n in source.notes])
        self.assertEqual(read_midi(write_midi(out)).tempo_map(),source.tempo_map())

    def test_invalid_and_empty(self):
        for config in [ReductionConfig(max_span=13),ReductionConfig(max_notes_per_hand=0),ReductionConfig(split_pitch=True)]:
            with self.assertRaises(ValueError):
                reduce_to_piano(score([(60,0,1)]),config)
        with self.assertRaises(ValueError):
            reduce_to_piano(score([]))

    def test_cli_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); original=root/'source.mid'; output=root/'piano.mid'; report=root/'report.json'
            original.write_bytes(write_midi(score([(48,0,1),(72,0,1)])))
            command=[sys.executable,'scripts/reduce_midi.py',str(original),'--output',str(output),'--report',str(report)]
            first=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            self.assertEqual(json.loads(report.read_text())['output_notes'],2)
            before=output.read_bytes()
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            self.assertEqual(output.read_bytes(),before)
