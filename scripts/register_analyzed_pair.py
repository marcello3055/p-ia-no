"""Operator-only cache registration; existing MP3 pair must already be stored."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.api.storage import Store
from services.api.training import register_analysis
p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,required=True);p.add_argument('--pair',required=True)
p.add_argument('--source-midi',type=Path,required=True);p.add_argument('--reference-midi',type=Path,required=True);p.add_argument('--provenance',type=Path,required=True)
a=p.parse_args()
print(json.dumps(register_analysis(Store(a.data_dir),a.pair,a.source_midi.read_bytes(),a.reference_midi.read_bytes(),json.loads(a.provenance.read_text())),ensure_ascii=False))
