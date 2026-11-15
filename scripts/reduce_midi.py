"""Agent-operated baseline reduction with explicit report and no overwrite."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.midi import MAX_BYTES, read_midi, write_midi
from packages.music.reduce import ReductionConfig, reduce_to_piano

parser=argparse.ArgumentParser(description='Redução experimental MIDI para piano.')
parser.add_argument('input',type=Path)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--report',type=Path,required=True)
parser.add_argument('--max-notes-per-hand',type=int,default=3)
parser.add_argument('--max-span',type=int,default=12)
parser.add_argument('--split-pitch',type=int,default=60)
args=parser.parse_args()
created=[]
try:
    if args.output.resolve()==args.report.resolve() or any(p.exists() for p in (args.output,args.report)):
        raise ValueError('Destinos devem ser distintos e novos; nenhum arquivo será sobrescrito.')
    with args.input.open('rb') as f:
        data=f.read(MAX_BYTES+1)
    output,report=reduce_to_piano(read_midi(data),ReductionConfig(args.split_pitch,args.max_notes_per_hand,args.max_span))
    encoded=write_midi(output)
    report['input_sha256']=hashlib.sha256(data).hexdigest()
    report['output_sha256']=hashlib.sha256(encoded).hexdigest()
    for path,payload in ((args.output,encoded),(args.report,(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())):
        with path.open('xb') as f:
            created.append(path)
            f.write(payload)
    print(f"Redução experimental: {report['input_notes']} → {report['output_notes']} notas. Sem áudio gerado.")
except Exception as exc:
    for path in created:
        path.unlink(missing_ok=True)
    print(f'Falha: {exc}',file=sys.stderr)
    sys.exit(1)
