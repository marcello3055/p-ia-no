import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from packages.music.population import initialize_population
from packages.music.ranking import rank_population,normalized_weights
from packages.music.midi import write_midi
from test_evaluate import score

class RankingTests(unittest.TestCase):
    def test_exact_reference_wins_with_explainable_contributions(self):
        source=score([(p,0,1) for p in [36,43,48,55,60,64,67,72,76,84]])
        ref=score([(36,0,1),(84,0,1)])
        report=rank_population(source,ref,initialize_population())
        self.assertEqual(report['evaluated'],100)
        self.assertEqual(report['best_score'],1)
        self.assertGreater(report['best_minus_baseline'],0)
        for row in report['results']:
            self.assertAlmostEqual(sum(row['contributions'].values()),row['score'])
            self.assertTrue(0<=row['score']<=1)
        best=[r for r in report['results'] if r['id'] in report['best_candidate_ids']]
        self.assertTrue(all(r['rank']==1 and r['criteria']['pitch_onset']==1 for r in best))
    def test_ties_cache_determinism(self):
        source=score([(72,0,1)])
        population=initialize_population(10)
        a=rank_population(source,source,population)
        self.assertEqual(a,rank_population(source,source,population))
        self.assertEqual(a['unique_evaluations'],1)
        self.assertEqual(len(a['best_candidate_ids']),10)
        self.assertTrue(all(r['rank']==1 for r in a['results']))
        self.assertEqual(a['ranking'],sorted(a['ranking']))
    def test_weights_and_validation(self):
        w={'pitch_onset':1,'duration':0,'pitch_classes':0,'attacks':0}
        r=rank_population(score([(60,0,1)]),score([(60,0,2)]),initialize_population(1),w)
        self.assertEqual(r['best_score'],1)
        self.assertEqual(r['results'][0]['criteria']['duration'],0)
        for value in [dict(w,attacks=-1),dict(w,attacks=float('nan')),dict(w,attacks=True),{},dict.fromkeys(w,0)]:
            with self.assertRaises(ValueError): normalized_weights(value)
    def test_no_reference_and_failed_candidates(self):
        with self.assertRaises(ValueError): rank_population(score([(60,0,1)]),score([]),initialize_population(1))
        with self.assertRaises(ValueError): rank_population(score([(60,0,1)]),score([(60,0,0)]),initialize_population(1))
        r=rank_population(score([]),score([(60,0,1)]),initialize_population(3))
        self.assertEqual(r['evaluated'],0); self.assertEqual(r['failed'],3)
        self.assertIsNone(r['best_score']); self.assertEqual(r['ranking'],[])
        self.assertTrue(all(row['rank'] is None and row['score'] is None for row in r['results']))
    def test_cli_checkpoint_replay_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder); source=p/'in.mid'; source.write_bytes(write_midi(score([(48,0,1),(72,0,1)])))
            cmd=[sys.executable,'scripts/rank_population.py',str(source),str(source),'--output-dir',str(p/'a'),'--size','3']
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            saved=(p/'a/ranking.json').read_bytes()
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            replay=subprocess.run([sys.executable,'scripts/rank_population.py',str(source),str(source),'--output-dir',str(p/'b'),'--population',str(p/'a/population.json')],capture_output=True,text=True)
            self.assertEqual(replay.returncode,0,replay.stderr)
            self.assertEqual(saved,(p/'b/ranking.json').read_bytes())
