"""Agent-operated CLI. Stop the API before CLI export/restore."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.api.backup import export_backup, restore_backup
from services.api.storage import Store

parser = argparse.ArgumentParser(description='Backup/restauração P-IA-NO; sem sobrescrever destinos.')
commands = parser.add_subparsers(dest='operation', required=True)
export = commands.add_parser('export')
export.add_argument('--data-dir', type=Path, required=True)
export.add_argument('--output', type=Path, required=True)
restore = commands.add_parser('restore')
restore.add_argument('--archive', type=Path, required=True)
restore.add_argument('--destination', type=Path, required=True)
args = parser.parse_args()
try:
    if args.operation == 'export':
        if not (args.data_dir / 'piano.sqlite3').is_file():
            raise ValueError('Banco de origem não encontrado.')
        result = export_backup(Store(args.data_dir), args.output)
    else:
        result = restore_backup(args.archive, args.destination)
    print(json.dumps(result))
except Exception as exc:
    print(f'Falha: {exc}', file=sys.stderr)
    sys.exit(1)
