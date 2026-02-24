import argparse
from pathlib import Path

from jobless.app import JoblessApp
from jobless.constants import APP_NAME, APP_VERSION
from jobless.commands import export, prune


def main() -> None:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="jobless - a simple job application manager for your terminal.",
        epilog="if no command is provided, the tui will run by default.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s v{APP_VERSION}",
    )

    subparsers = parser.add_subparsers(dest="command", help="commands")

    prune_parser = subparsers.add_parser(
        "prune",
        help="remove stale applications and orphan records.",
    )
    prune_parser.add_argument(
        "--days",
        type=int,
        default=180,
        help="prune stale applications older than this (default: 180)",
    )
    prune_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what records would be deleted.",
    )
    prune_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="skip confirmation prompt.",
    )

    export_parser = subparsers.add_parser(
        "export",
        help="export your data to a csv or zip file.",
    )
    export_parser.add_argument(
        "-f",
        "--file",
        help="destination path (must end in .csv or .zip).",
        required=True,
    )
    export_parser.add_argument(
        "--only",
        choices=["contacts", "companies", "applications", "all"],
        default="all",
        help="specify what to export (default: all).",
    )

    args = parser.parse_args()

    if not args.command:
        app = JoblessApp()
        app.run()
        return

    if args.command == "prune":
        prune(
            days=args.days,
            dry_run=args.dry_run,
            confirm=args.yes,
        )
    elif args.command == "export":
        file_path: Path = Path(args.file)
        if args.only == "all" and file_path.suffix != ".zip":
            parser.error(
                f"exporting 'all' requires a .zip extension to avoid errors. got '{file_path.name}'"
            )

        if args.only != "all" and file_path.suffix != ".csv":
            parser.error(
                f"exporting {args.type} requires a .csv extension. got '{file_path.name}'"
            )

        if file_path.exists():
            confirm = input(
                f"⚠️ file '{file_path.name}' already exists. overwrite? [y/N]:"
            )
            if confirm.lower() != "y":
                print("aborted!")
                return

        export(file_path, scope=args.only)
