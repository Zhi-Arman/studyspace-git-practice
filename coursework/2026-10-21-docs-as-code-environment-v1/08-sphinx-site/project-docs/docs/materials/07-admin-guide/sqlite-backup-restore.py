"""Create a backup and restored candidate without replacing the source or existing files.

Restricted to this learning packet. It does not activate restored data or implement
StudySpace domain migration, retention, account verification or production recovery.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

PACKET = Path(__file__).resolve().parent.parent


def in_packet(value):
    path = Path(value).expanduser().resolve()
    if not path.is_relative_to(PACKET):
        raise ValueError('All paths must remain inside the independent learning packet')
    return path


def integrity(connection):
    rows = connection.execute('PRAGMA integrity_check').fetchall()
    if rows != [('ok',)]:
        raise ValueError('SQLite integrity_check failed; no activation is performed')


def copy_database(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental overwrite, including after a prior run.
    with target.open('xb'):
        pass
    try:
        with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as src:
            with sqlite3.connect(target) as dst:
                src.backup(dst)
                integrity(dst)
    except Exception:
        # Retain the failed candidate for diagnosis; never remove/replace input files.
        raise RuntimeError('Candidate creation failed; inspect the output before reuse') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--backup', required=True)
    parser.add_argument('--restore', required=True)
    args = parser.parse_args()
    source, backup, restored = map(in_packet, (args.source, args.backup, args.restore))
    if len({source, backup, restored}) != 3:
        raise ValueError('Source, backup and restored candidate must be distinct')
    if not source.is_file():
        raise ValueError('Source database must exist; an empty replacement is never created')
    if backup.exists() or restored.exists():
        raise FileExistsError('Output exists; choose fresh names, no overwrite is allowed')
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as connection:
        integrity(connection)
    copy_database(source, backup)
    copy_database(backup, restored)
    after = hashlib.sha256(source.read_bytes()).hexdigest()
    if before != after:
        raise RuntimeError('Source changed during the exercise; do not activate the candidate')
    print(json.dumps({'backup_integrity': 'ok', 'restored_integrity': 'ok',
                      'source_unchanged': True, 'activation': 'NOT_RUN',
                      'domain_acceptance': 'NOT_RUN'}, indent=2))


if __name__ == '__main__':
    main()
