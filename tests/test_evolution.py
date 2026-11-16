import copy
import unittest
from packages.music.population import initialize_population,load_population
from packages.music.ranking import rank_population
from packages.music.evolution import next_generation
from test_evaluate import score

class EvolutionTests(unittest.TestCase):
    def setUp(self):
        self.source=score([(p,0,1) for p in [36,43,48,55,60,64,67,72,76,84]])
        self.ref=score([(36,0,1),(84,0,1)])
        self.pop=initialize_population();self.rank=rank_population(self.source,self.ref,self.pop)
    def test_elitism_diversity_bounds_and_determinism(self):
        original=copy.deepcopy(self.pop)
        out=next_generation(self.pop,self.rank,seed=42,mutation_rate=1)
        self.assertEqual(out,next_generation(self.pop,self.rank,seed=42,mutation_rate=1))
        self.assertEqual(self.pop,original)
        items=load_population(out);ids={i.id for i in items}
        self.assertEqual(len(ids),100);self.assertEqual(out['generation'],1)
        self.assertIn(self.rank['ranking'][0],ids)
        self.assertEqual(out['candidates'][0],self.pop['candidates'][0])
        lineage=out['evolution']['lineage']
        self.assertEqual(sum(r['origin']=='immigrant' for r in lineage),10)
        self.assertTrue(any(r['origin']=='offspring' and r['mutated_gene'] is not None for r in lineage))
        after=rank_population(self.source,self.ref,out)
        self.assertGreaterEqual(after['best_score'],self.rank['best_score'])
        self.assertEqual(after['generation'],1)
    def test_reject_diagnostics_and_mismatched_rankings(self):
        for change in [{'training_allowed':False},{'status':'rejected_by_user'},{'generation':8},{'population_sha256':'bad'}]:
            with self.assertRaises(ValueError):next_generation(self.pop,{**self.rank,**change})
        with self.assertRaises(ValueError):next_generation(self.pop,{**self.rank,'results':[]})
    def test_invalid_config(self):
        for kw in [{'mutation_rate':float('nan')},{'elite_count':0},{'seed':True},{'immigrant_count':100},{'elite_count':100}]:
            with self.assertRaises(ValueError):next_generation(self.pop,self.rank,**kw)
    def test_full_space_terminates(self):
        pop=initialize_population(390);r=rank_population(self.source,self.ref,pop)
        out=next_generation(pop,r)
        self.assertEqual(len(load_population(out)),390)
        self.assertLessEqual(out['evolution']['attempts'],7800)
    def test_all_failed_no_reproduction(self):
        r=rank_population(score([]),self.ref,self.pop)
        with self.assertRaises(ValueError):next_generation(self.pop,r)
