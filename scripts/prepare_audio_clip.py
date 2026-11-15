"""Agent-operated preparation: the user can supply a complete audio file."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.audio_clip import prepare_clip
parser=argparse.ArgumentParser(description='Preparar trecho curto para análise musical experimental.')
parser.add_argument('input',type=Path)
parser.add_argument('--output-dir',type=Path,required=True)
parser.add_argument('--start',type=float,default=0)
parser.add_argument('--seconds',type=float,default=20)
args=parser.parse_args()
try:
    print(json.dumps(prepare_clip(args.input,args.output_dir,args.start,args.seconds),ensure_ascii=False,indent=2))
except (ValueError,RuntimeError,OSError) as exc:
    print(f'Falha: {exc}',file=sys.stderr); sys.exit(1)
