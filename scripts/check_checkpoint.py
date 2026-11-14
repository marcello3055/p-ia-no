"""Validate preparation files; this is not a music test."""
from pathlib import Path
import json
root = Path(__file__).resolve().parents[1]
required = ['README.md','PROGRESS.md','ARCHITECTURE.md','TODO.md','.gitignore',
            'docs/RESEARCH.md','docs/REQUIREMENTS.md','docs/RECOVERY.md']
for name in required:
    assert (root / name).is_file(), name
    assert (root / name).read_text().strip(), name
config = json.loads((root / 'configs/project.json').read_text())
assert config['allow_paid_compute'] is False
assert config['transcription_enabled'] is False
assert config['population_size'] == 100
print('PASS: preparation files and safe planning defaults. No musical functionality tested.')
