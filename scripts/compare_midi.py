"""Agent-operated comparison; no overwrite and no musical-quality claims."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from packages.music.midi import MAX_BYTES, read_midi
from packages.music.evaluate import EvaluationConfig, evaluate

parser = argparse.ArgumentParser(description='Correspondência simbólica entre dois MIDIs.')
parser.add_argument('reference', type=Path)
parser.add_argument('candidate', type=Path)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--time-unit', choices=['quarters', 'seconds'], default='quarters')
parser.add_argument('--onset-tolerance', type=float, default=.1)
parser.add_argument('--duration-tolerance', type=float, default=.1)
parser.add_argument('--duration-relative', type=float, default=.2)
parser.add_argument('--include-percussion', action='store_true')
args = parser.parse_args()
def load(path):
    with path.open('rb') as source:
        return read_midi(source.read(MAX_BYTES + 1))
try:
    if args.output.exists():
        raise ValueError('O relatório já existe; escolha um destino novo.')
    config = EvaluationConfig(args.time_unit, args.onset_tolerance, args.duration_tolerance,
                              args.duration_relative, args.include_percussion)
    result = evaluate(load(args.reference), load(args.candidate), config)
    with args.output.open('x') as output:
        json.dump(result, output, ensure_ascii=False, indent=2, allow_nan=False)
        output.write('\n')
    print(f"{result['counts']['matched_pitch_onset']} correspondências. Relatório salvo; sem avaliação artística.")
except Exception as exc:
    print(f'Falha: {exc}', file=sys.stderr)
    sys.exit(1)
