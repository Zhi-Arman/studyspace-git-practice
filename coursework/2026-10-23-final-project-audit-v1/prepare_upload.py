"""Copy source and evidence without caches, secrets, Git metadata or submodules.

Usage: python3 prepare_upload.py PROJECT_ROOT EXISTING_UPLOAD_CHECKOUT
The existing checkout must be on the explicitly chosen upload branch.
Local originals and excluded files are never deleted.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
destination = Path(sys.argv[2]).resolve()
if root == destination or root in destination.parents:
    raise SystemExit('Use a separate checkout outside the source project.')
data = root / 'coursework/2026-10-23-final-project-audit-v1/data'
pruned = {
    '.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', '.ruff_cache',
    '.gstack', 'uv-cache', 'npm-cache', 'fonts', 'fontcache', 'font-cache',
    'pytest-temp', 'pytest-tmp', 'site', 'dist', '_build', 'backups', 'final-render',
}
paths = []
excluded = []
for directory, directories, files in os.walk(root):
    kept = []
    for name in directories:
        path = Path(directory) / name
        if (name in pruned or name.endswith('.git')
                or name.startswith(('render', 'font-probe'))):
            excluded.append({'path': str(path.relative_to(root)) + '/', 'reason': 'local/generated directory'})
        elif path.is_symlink():
            excluded.append({'path': str(path.relative_to(root)), 'reason': 'symlink'})
        else:
            kept.append(name)
    directories[:] = kept
    for name in files:
        path = Path(directory) / name
        relative = str(path.relative_to(root))
        if name == '.git' or path.is_symlink():
            excluded.append({'path': relative, 'reason': 'Git metadata or symlink'})
        else:
            paths.append(relative)

raw = b'\0'.join(path.encode() for path in paths) + b'\0'
check = subprocess.run(
    ['git', 'check-ignore', '--no-index', '--stdin', '-z'],
    input=raw, capture_output=True, cwd=root, check=False,
)
if check.returncode not in {0, 1}:
    raise SystemExit(check.stderr.decode())
ignored = set(check.stdout.decode().split('\0'))
records = []
for relative in sorted(paths):
    if relative in ignored:
        excluded.append({'path': relative, 'reason': 'gitignore'})
        continue
    source = root / relative
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise SystemExit('Copy hash mismatch: ' + relative)
    if relative not in {
        'coursework/2026-10-23-final-project-audit-v1/data/upload-manifest.json',
        'coursework/2026-10-23-final-project-audit-v1/data/excluded-paths.json',
        'coursework/2026-10-23-final-project-audit-v1/data/sensitive-scan.json',
        'coursework/2026-10-23-final-project-audit-v1/data/package-verification.json',
        'coursework/2026-10-23-final-project-audit-v1/data/publication.json',
    }:
        records.append({'path': relative, 'bytes': source.stat().st_size, 'sha256': digest})

manifest = {
    'date': '2026-10-23', 'branch': 'docs/course-project-package',
    'description': 'Source and selected evidence; hashes exclude self-referential and post-upload metadata.',
    'file_count': len(records), 'bytes': sum(x['bytes'] for x in records), 'files': records,
}
(data / 'upload-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(data / 'excluded-paths.json').write_text(json.dumps(excluded, ensure_ascii=False, indent=2) + '\n')
for name in ['upload-manifest.json', 'excluded-paths.json']:
    target = destination / 'coursework/2026-10-23-final-project-audit-v1/data' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(data / name, target)
print(json.dumps({'copied_files': len(records), 'bytes': manifest['bytes'],
                  'excluded_paths_or_directories': len(excluded)}, ensure_ascii=False))
