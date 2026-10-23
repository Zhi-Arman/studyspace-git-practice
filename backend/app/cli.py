"""Explicit local initialization/admin/maintenance commands; no default passwords."""

import argparse
import getpass
import json
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings
from app.database import create_db_engine
from app.maintenance import backup, cleanup, create_admin, restore, seed_demo
from app.migration import migrate


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="StudySpace local maintenance")
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser(
        "init-local", help="Migrate and add explicitly synthetic resources"
    )
    initialize.add_argument("--no-demo", action="store_true")
    admin = commands.add_parser(
        "create-admin", help="Create an administrator without a default password"
    )
    admin.add_argument("--username", required=True)
    admin.add_argument("--name", required=True)
    admin.add_argument("--password-file", type=Path)
    commands.add_parser("cleanup")
    saving = commands.add_parser("backup")
    saving.add_argument("--output", required=True, type=Path)
    restoring = commands.add_parser("restore")
    restoring.add_argument("--backup", required=True, type=Path)
    restoring.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    engine = create_db_engine(Settings())
    try:
        if args.command == "init-local":
            migrate(engine)
            result = seed_demo(engine) if not args.no_demo else {"migrated": True}
        elif args.command == "create-admin":
            migrate(engine)
            if args.password_file:
                if args.password_file.stat().st_mode & 0o077:
                    raise ValueError("Password file must have private permissions (chmod 600).")
                password = args.password_file.read_text().rstrip("\r\n")
            else:
                password = getpass.getpass("Administrator password (10–128 characters): ")
                if password != getpass.getpass("Repeat password: "):
                    raise ValueError("Passwords do not match.")
            create_admin(engine, args.username, args.name, password)
            result = {"administrator_created": True}
        elif args.command == "cleanup":
            result = cleanup(engine)
        elif args.command == "backup":
            result = {"backup": str(backup(engine, args.output))}
        else:
            result = {"restored": str(restore(args.backup, args.output))}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except ValidationError:
        print("Invalid account fields; username/name/password policy was not met.", file=sys.stderr)
        return 2
    except (OSError, ValueError, SQLAlchemyError):
        print(
            "Local operation failed. Check paths, permissions and initialized database; "
            "existing files/accounts are never overwritten.",
            file=sys.stderr,
        )
        return 2
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
