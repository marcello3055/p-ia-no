"""Controlled checks for diagnostic scores and listening snippet boundaries."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tempfile
import wave
import numpy as np
from experiments.review_alignment import compare, listening

def note(pitch,start=0,end=1):
    return dict(pitch=pitch,start_seconds=start,end_seconds=end,activation=1.)
mapping=[[0,20],[1,21]]
a=compare([note(60)],[note(60)],mapping,0,1,20)
assert a['note_chroma_cosine']==1 and a['attack_hit_fraction']==1
b=compare([note(60)],[note(61)],mapping,0,1,20)
assert b['note_chroma_cosine']==0 and b['attack_hit_fraction']==0
c=compare([note(60)],[],mapping,0,1,20)
assert c['note_chroma_cosine'] is None and c['active_sample_fraction']==0
# A pitch-class match intentionally ignores octave; this must not be called melody accuracy.
assert compare([note(60)],[note(72)],mapping,0,1,20)['note_chroma_cosine']==1
with tempfile.TemporaryDirectory() as d:
    root=Path(d);(root/'source').mkdir();pcm=np.arange(8000,dtype=np.int16)
    with wave.open(str(root/'source/clip.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(pcm.tobytes())
    timeline=listening(root,[('source',.25,.75,'test')],root/'out.wav')
    with wave.open(str(root/'out.wav'),'rb') as w:
        assert w.getnframes()==12000
        data=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16)
        assert np.array_equal(data[:4000],pcm[2000:6000]) and not data[4000:].any()
    assert timeline[0]['ends_in_comparison']==.5
    try: listening(root,[('source',0,2,'invalid')],root/'bad.wav')
    except ValueError: pass
    else: raise AssertionError('Invalid boundary accepted')
print('PASS: matching/different/octave notes, missing evidence, exact PCM crops, silence and invalid bounds.')
