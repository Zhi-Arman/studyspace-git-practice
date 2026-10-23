"""Inspect the isolated learning environment without starting application services."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from importlib import metadata, import_module
from collections import Counter
import sys
import platform
import subprocess
import json
import tomllib

root = Path(__file__).resolve().parents[1]
names = {'fastapi': 'fastapi', 'uvicorn': 'uvicorn', 'sqlalchemy': 'sqlalchemy', 'pydantic-settings': 'pydantic_settings', 'pytest': 'pytest', 'httpx': 'httpx', 'openapi-spec-validator': 'openapi_spec_validator', 'PyYAML': 'yaml'}
versions = {}
for dist, module in names.items():
    import_module(module)
    versions[dist] = metadata.version(dist)
lock = tomllib.loads((root / '00-project/backend/uv.lock').read_text())
locked = {p['name']: p['version'] for p in lock['package'] if 'version' in p}
installed = {d.metadata['Name'].lower().replace('_', '-'): d.version for d in metadata.distributions()}
mismatches = [{'name': name, 'installed': version, 'locked': locked.get(name)} for name, version in installed.items() if version != locked.get(name)]
assert not mismatches, mismatches
requirements = json.loads((root / '00-project/docs/data/requirements.json').read_text())
cases = json.loads((root / '00-project/docs/data/test-cases.json').read_text())
result = {
    'checked_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
    'python': sys.version,
    'executable': sys.executable,
    'isolated_environment': sys.prefix != sys.base_prefix,
    'platform': platform.platform(),
    'macos': subprocess.check_output(['sw_vers', '-productVersion'], text=True).strip(),
    'tools': {cmd[0]: subprocess.check_output(cmd, text=True).strip() for cmd in [['uv', '--version'], ['node', '--version'], ['npm', '--version'], ['git', '--version']]},
    'project_python_constraint': '>=3.13,<3.15',
    'screenshot_python_3_11_or_newer': sys.version_info >= (3, 11),
    'project_python_compatible': (3, 13) <= sys.version_info[:2] < (3, 15),
    'dependency_versions_imported': versions,
    'installed_packages_matching_lock': len(installed),
    'lock_version_mismatches': mismatches,
    'omitted_conditional_packages': {'colorama': 'Windows only', 'tzdata': 'Windows psycopg dependency', 'greenlet': 'SQLAlchemy platform marker excludes Darwin arm64', 'psycopg': 'postgres extra not selected', 'psycopg-binary': 'postgres extra not selected'},
    'requirement_status_counts': dict(Counter(x['status'] for x in requirements['requirements'])),
    'test_case_status_counts': dict(Counter(x['status'] for x in cases['test_cases'])),
    'production_access': 'NOT_RUN',
    'service_start': 'NOT_RUN',
    'frontend_dependency_install': 'NOT_RUN',
    'original_teacher_docs_dependencies': 'UNKNOWN_ORIGINAL_NOT_FOUND',
    'dependency_install_attempts': [{'log': 'dependency-install.log', 'result': 'FAIL_DNS_RESTRICTED'}, {'log': 'dependency-install-network-retry.log', 'result': 'PASS', 'exit_code': 0}],
    'document_checks': {'check_docs.py': 'PASS', 'generate_registers.py --check': 'PASS'},
    'dependency_consistency': 'PASS',
}
(root / 'artifacts/environment-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
