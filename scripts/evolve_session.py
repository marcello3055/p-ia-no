"""Run or resume a bounded symbolic evolution session."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from packages.music.midi import MAX_BYTES
from packages.music.session import run_session
from packages.music.evaluate import EvaluationConfig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('reference', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--until', type=int, required=True)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--evaluation-config', type=Path, help='JSON de tolerâncias; omitido na retomada reutiliza configuração salva.')
    args = parser.parse_args()
    def read(path):
        with path.open('rb') as handle:
            return handle.read(MAX_BYTES + 1)
    try:
        config = EvaluationConfig(**json.loads(args.evaluation_config.read_text())) if args.evaluation_config else None
        result = run_session(read(args.source), read(args.reference), args.output_dir,
                             args.until, resume=args.resume, seed=args.seed, evaluation_config=config)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(f'Falha: {exc}. Checkpoints completos preservados.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
