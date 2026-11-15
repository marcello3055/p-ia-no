"""Agent-operated offline rendering; no manual setup required from the user."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.render import DEFAULT_SOUNDFONT, render_piano
parser=argparse.ArgumentParser(description='Renderizar MIDI reduzido em piano WAV e MP3.')
parser.add_argument('input',type=Path)
parser.add_argument('--output-dir',type=Path,required=True)
parser.add_argument('--soundfont',type=Path,default=DEFAULT_SOUNDFONT)
args=parser.parse_args()
try:
    r=render_piano(args.input,args.output_dir,args.soundfont)
    print(f"WAV e MP3 gerados: {r['duration_seconds']:.2f}s; {r['notes']} notas. Qualidade auditiva ainda não avaliada.")
except Exception as exc:
    print(f'Falha: {exc}',file=sys.stderr); sys.exit(1)
