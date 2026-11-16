import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from packages.music.population import initialize_population,load_population,generate_proposals,SPACE
from packages.music.midi import read_midi,write_midi
from test_evaluate import score

class PopulationTests(unittest.TestCase):
    def test_default_unique_reproducible_and_baseline(self):
        a=initialize_population()
        self.assertEqual(a,initialize_population())
        items=load_population(a)
        self.assertEqual(len({i.id for i in items}),100)
        self.assertEqual(items[0].config.split_pitch,60)
        self.assertEqual(items[0].config.max_notes_per_hand,3)
        self.assertNotEqual(a['candidates'][1:],initialize_population(seed=42)['candidates'][1:])
        self.assertEqual(len(load_population(initialize_population(len(SPACE)))),390)
    def test_config_validation_and_manifest_tampering(self):
        for size in [0,391,True,1.5]:
            with self.assertRaises(ValueError): initialize_population(size)
        with self.assertRaises(ValueError): initialize_population(seed=-1)
        a=initialize_population(2); a['candidates'][1]['config']['max_span']=0
        with self.assertRaises(ValueError): load_population(a)
        a=initialize_population(2); a['candidates'][1]=a['candidates'][0]
        with self.assertRaises(ValueError): load_population(a)
    def test_all_candidates_generate_valid_midi_without_mutation(self):
        source=score([(p,t,1) for t in [0,1,2] for p in [36,43,48,55,60,64,67,72,76,84]])
        before=copy.deepcopy(source); results=list(generate_proposals(source,initialize_population()))
        self.assertEqual(len(results),100); self.assertEqual(source,before)
        for row,midi in results:
            self.assertEqual(row['status'],'generated'); self.assertIsNone(row['score'])
            self.assertEqual(len(read_midi(midi).notes),row['output_notes'])
        self.assertGreater(len({row['musical_sha256'] for row,_ in results}),1)
    def test_duplicate_music_is_reported_and_empty_source_fails(self):
        results=list(generate_proposals(score([(72,0,1)]),initialize_population(5)))
        self.assertEqual(len({row['musical_sha256'] for row,_ in results}),1)
        self.assertTrue(all(row['status']=='failed' and midi is None for row,midi in generate_proposals(score([]),initialize_population(3))))
    def test_cli_replay_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); src=root/'input.mid'; src.write_bytes(write_midi(score([(48,0,1),(72,0,1)])))
            command=[sys.executable,'scripts/create_population.py',str(src),'--output-dir',str(root/'a'),'--size','4']
            first=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            repeat=subprocess.run(command,capture_output=True); self.assertNotEqual(repeat.returncode,0)
            replay=subprocess.run([sys.executable,'scripts/create_population.py',str(src),'--output-dir',str(root/'b'),'--population',str(root/'a/population.json')],capture_output=True,text=True)
            self.assertEqual(replay.returncode,0,replay.stderr)
            self.assertEqual((root/'a/results.json').read_bytes(),(root/'b/results.json').read_bytes())
            self.assertEqual(json.loads(first.stdout)['evaluated'],0)
