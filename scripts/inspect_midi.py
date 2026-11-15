"""Agent-operated MIDI inspection; user does not need to run commands."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from packages.music.midi import MAX_BYTES, read_midi, write_midi
parser = argparse.ArgumentParser()
parser.add_argument('input', type=Path)
parser.add_argument('--json', type=Path, required=True)
parser.add_argument('--midi', type=Path)
args = parser.parse_args()
try:
    targets = [args.json] + ([args.midi] if args.midi else [])
    if len({p.resolve() for p in targets}) != len(targets) or any(p.exists() for p in targets):
        raise ValueError('Destinos devem ser novos e distintos.')
    with args.input.open('rb') as stream:
        score = read_midi(stream.read(MAX_BYTES + 1))
    representation = json.dumps(score.to_dict(), ensure_ascii=False, indent=2)
    midi_bytes = write_midi(score) if args.midi else None
    with args.json.open('x') as stream:
        stream.write(representation + '\n')
    if args.midi:
        with args.midi.open('xb') as stream:
            stream.write(midi_bytes)
    print(f'{len(score.notes)} notas; {len(score.track_ends)} trilhas. Nenhum áudio foi gerado.')
except Exception as exc:
    print(f'Falha: {exc}', file=sys.stderr)
    sys.exit(1)
