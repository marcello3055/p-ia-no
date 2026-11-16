"""Agent-operated private evolution backup/restore CLI."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.session_backup import export_session, restore_session

p = argparse.ArgumentParser()
sub = p.add_subparsers(dest='action', required=True)
e = sub.add_parser('export')
for flag in ('session', 'source', 'reference', 'output'):
    e.add_argument('--'+flag, type=Path, required=True)
r = sub.add_parser('restore')
r.add_argument('--archive', type=Path, required=True)
r.add_argument('--destination', type=Path, required=True)
a = p.parse_args()
try:
    result = (export_session(a.session, a.source, a.reference, a.output) if a.action == 'export'
              else restore_session(a.archive, a.destination))
    print(json.dumps(result, ensure_ascii=False))
except Exception as exc:
    print(f'Falha: {exc}', file=sys.stderr)
    sys.exit(1)
