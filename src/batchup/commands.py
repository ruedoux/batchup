from argparse import Namespace
import argparse
import getpass
import os
import tempfile
from batchup.backup.backup_creator import BackupCreator
from batchup.backup.remote_backup import RemoteBackup
from batchup.config import Config
from batchup.logger import SimpleLogger


class Commands:

    def __init__(self, logger: SimpleLogger) -> None:
        self.logger = logger

    def backup(self, args: Namespace) -> None:
        self.logger.info(f"Running backup...")
        config_path: str = args.config
        if not os.path.isfile(config_path):
            self.logger.error(f"Configuration does not exist: {config_path}")
            exit(1)

        config = Config(config_path)
        with tempfile.TemporaryDirectory() as temp_dir_path:
            local_backup_path = config.local_backup_path
            local_backup_name = config.local_backup_name
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

            self.logger.info(f"Local backup path: {config.local_backup_path}")
            self.logger.debug("Local include paths:")
            for path in includes:
                self.logger.debug(f"\t{path}")
            self.logger.debug("Local exclude paths:")
            for path in excludes:
                self.logger.debug(f"\t{path}")
            password = getpass.getpass(prompt="Input password: ")
            backup_creator = BackupCreator(logger=self.logger)
            backup_creator.backup_local(
                local_backup_path=local_backup_path,
                local_backup_name=local_backup_name,
                include_file_path=include_file_path,
                exclude_file_path=exclude_file_path,
                password=password,
            )

        self.logger.info(f"Done!")

    def pull(self, args: Namespace) -> None:
        self.logger.info(f"Running pull...")
        config_path: str = args.config
        if not os.path.isfile(config_path):
            self.logger.error(f"Configuration does not exist: {config_path}")
            exit(1)

        config = Config(config_path)
        local_backup_path = config.local_backup_path
        local_backup_name = config.local_backup_name
        remote_backup_paths = config.remote_backup_paths

        self.logger.info(f"Pulling remote repositories to: {config.local_backup_path}")
        self.logger.info("Remote targets:")
        for backup_path in remote_backup_paths:
            self.logger.info(f"\t{backup_path}")

        backup_creator = BackupCreator(logger=self.logger)
        backup_creator.pull_remote_repositories(
            local_backup_path=local_backup_path,
            local_backup_name=local_backup_name,
            remote_backup_paths=remote_backup_paths,
        )

        self.logger.info(f"Done!")

    def push(self, args: Namespace) -> None:
        self.logger.info(f"Running push...")
        config_path: str = args.config
        if not os.path.isfile(config_path):
            self.logger.error(f"Configuration does not exist: {config_path}")
            exit(1)

        config = Config(config_path)
        local_backup_path = config.local_backup_path
        remote_backup_paths = config.remote_backup_paths

        self.logger.info(f"Pushing local repositories: {config.local_backup_path}")
        backup_creator = BackupCreator(logger=self.logger)
        backup_creator.push_local_repositories(
            local_backup_path=local_backup_path,
            remote_backup_paths=remote_backup_paths,
        )

        self.logger.info(f"Done!")

    def remote(self, args: Namespace) -> None:
        self.logger.info(f"Running remote backup...")
        config_path: str = args.config
        if not os.path.isfile(config_path):
            self.logger.error(f"Configuration does not exist: {config_path}")
            exit(1)

        config = Config(config_path)
        RemoteBackup(logger=self.logger).run(config)

        self.logger.info(f"Done!")

    def parse_commands(self) -> None:
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
        backup_parser.set_defaults(func=self.backup)

        pull_parser = subparsers.add_parser(
            "pull", parents=[main_parser], help="Pull remote repositories"
        )
        pull_parser.set_defaults(func=self.pull)

        push_parser = subparsers.add_parser(
            "push", parents=[main_parser], help="Push to remote repositories"
        )
        push_parser.set_defaults(func=self.push)

        remote_parser = subparsers.add_parser(
            "remote", parents=[main_parser], help="Remote backup"
        )
        remote_parser.set_defaults(func=self.remote)

        args = parser.parse_args()
        args.func(args)
