"""Create a reproducible synthetic session for browser audio QA, never Tifa training."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.midi import Note, Event, Score, write_midi
from packages.music.session import run_session


def midi(values):
    notes=[Note(i,0,pitch,80,0,round(start*1000),round((start+duration)*1000),1,2)
           for i,(pitch,start,duration) in enumerate(values)]
    return write_midi(Score(1000,1,[n.end_tick for n in notes],notes,
                           [Event(0,0,0,True,{'type':'set_tempo','tempo':500000})],[]))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    source=[];reference=[]
    for beat,top in enumerate([72,76,79,76,74,72,71,72]):
        source.extend([(pitch,beat,0.9) for pitch in [36,48,55,60,64,top]])
        reference.extend([(36,beat,0.9),(top,beat,0.9)])
    source_bytes=midi(source);reference_bytes=midi(reference)
    result=run_session(source_bytes,reference_bytes,args.output,1)
    (args.output/'source.mid').write_bytes(source_bytes)
    (args.output/'reference.mid').write_bytes(reference_bytes)
    (args.output/'DEMO.txt').write_text('Exemplo sintético para testar o player. Não é Tifa nem evidência de aprendizagem musical.\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
