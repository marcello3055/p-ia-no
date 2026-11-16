import unittest
from packages.music.time_map import warp_reference
class TimeMapTests(unittest.TestCase):
    def test_shift_and_tempo(self):
        score,stats=warp_reference([{'start_seconds':1,'end_seconds':3,'pitch':60}],[[0,10],[1,12],[2,14]],10)
        self.assertEqual((score.notes[0].start_tick,score.notes[0].end_tick),(480,1440))
        self.assertEqual(stats['mapped_notes'],1)
    def test_edges_and_plateau(self):
        notes=[{'start_seconds':0,'end_seconds':1,'pitch':60},{'start_seconds':1,'end_seconds':5,'pitch':64}]
        score,stats=warp_reference(notes,[[0,2],[1,2],[2,4]],0)
        self.assertEqual(stats['excluded_outside_mapping'],1)
        self.assertEqual(stats['clipped_at_boundaries'],1)
        self.assertEqual((score.notes[0].start_tick,score.notes[0].end_tick),(480,1920))
    def test_bad_maps(self):
        for mapping in [[],[[0,2],[1,1]],[[0,1],[0,2]],[[0,1],[1,1]],[[0,1],[1,float('nan')]]]:
            with self.assertRaises(ValueError): warp_reference([],mapping,0)
