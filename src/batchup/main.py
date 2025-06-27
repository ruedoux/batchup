from argparse import Namespace
import argparse
import os
import tempfile
from batchup.backup.backup_creator import BackupCreator
from batchup.config import Config
from batchup.init import Init
from batchup.logger import SimpleLogger


logger = SimpleLogger(level="DEBUG")


def run(args: Namespace) -> None:
    logger.info(f"Running backup...")
    config_path: str = args.config
    config = Config(config_path)
    with tempfile.TemporaryDirectory() as temp_dir_path:
        root_path = config.root_path
        local_backup_name = config.local_backup_name
        external_backup_paths = config.external_backup_paths
        include_file_path = f"{temp_dir_path}/i.txt"
        exclude_file_path = f"{temp_dir_path}/e.txt"
        includes = config.includes.copy()
        excludes = config.excludes.copy()

        excludes = excludes + config.matched_excludes
        with open(include_file_path, "w") as f:
            for line in includes:
                f.write(line + "\n")
        with open(exclude_file_path, "w") as f:
            for line in excludes:
                f.write(line + "\n")

        logger.info(f"Local target: {config.root_path}")
        logger.info("Local include paths:")
        for path in includes:
            logger.info(f"\t{path}")
        logger.info("Local exclude paths:")
        for path in excludes:
            logger.info(f"\t{path}")
        logger.info("Copy external targets:")
        for backup_path in external_backup_paths:
            logger.info(f"\t{backup_path}")

        BackupCreator(logger=logger).backup(
            root_path,
            local_backup_name,
            external_backup_paths,
            include_file_path,
            exclude_file_path,
        )

    logger.info(f"Done!")


def parse_commands() -> None:
    home_dir = os.path.expanduser("~")
    dir_path = os.path.join(home_dir, ".config", "batchup")
    default_config_path = os.path.join(dir_path, "config.json")

    main_parser = argparse.ArgumentParser(add_help=False)
    main_parser.add_argument(
        "-c", "--config", default=default_config_path, help="Path to config file"
    )
    parser = argparse.ArgumentParser(
        description="A toolset for GNU/Linux",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    backup_parser = subparsers.add_parser(
        "backup", parents=[main_parser], help="Run the backup routine"
    )
    backup_parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


def main() -> None:
    init = Init(logger)
    init.check_requirements()
    init.prepare_config()
    parse_commands()


if __name__ == "__main__":
    main()
