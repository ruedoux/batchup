import os
import subprocess

from batchup.backup.restic import Restic
from batchup.logger import SimpleLogger
from batchup.utils import Utils


class BackupCreator:
    def __init__(self, logger: SimpleLogger) -> None:
        self.logger = logger
        self.restic = Restic(logger)

    def backup_local(
        self,
        root_path: str,
        local_backup_name: str,
        include_file_path: str,
        exclude_file_path: str,
        password: str,
    ) -> None:
        if not os.path.exists(include_file_path):
            self.logger.error(f"File does not exist '{include_file_path}'")
            return
        if not os.path.exists(exclude_file_path):
            self.logger.error(f"File does not exist '{include_file_path}'")
            return

        self._check_root_directory(root_path)

        backup_target_path = os.path.join(root_path, local_backup_name)

        if not self.restic.backup_repository(
            backup_target_path=backup_target_path,
            include_file_path=include_file_path,
            exclude_file_path=exclude_file_path,
            password=password,
        ):
            self.logger.error("Failed to create restic backup. Aborting.")
            exit(1)

    def backup_remote(
        self, root_path: str, local_backup_name: str, external_backup_paths: list[str]
    ) -> None:
        self._check_root_directory(root_path)
        backup_target_path = os.path.join(root_path, local_backup_name)

        self._pull_remote_repositories(
            root_path, local_backup_name, external_backup_paths
        )
        self._push_local_repository(
            backup_target_path=backup_target_path,
            local_backup_name=local_backup_name,
            external_backup_paths=external_backup_paths,
        )

    def _check_root_directory(self, root_path: str) -> None:
        if not os.path.exists(root_path):
            self.logger.info("Did not detect root folder for repositiories.")
            self.logger.info("Creating folder: '{root_path}'")
            os.makedirs(name=root_path)

    def _pull_remote_repositories(
        self, root_path: str, local_backup_name: str, external_backup_paths: list[str]
    ) -> None:
        if len(external_backup_paths) == 0:
            self.logger.info("No remote repositories, skipping pull.")
            return

        self.logger.info(msg="Pulling remote repositories to local repository...")
        for external_backup_path in external_backup_paths:
            if not Utils.has_server_connection(external_backup_path):
                self.logger.error(
                    f"Could not establish connection to: '{external_backup_path}'"
                )
                continue

            external_repo_names = self._get_repositories_from_root(external_backup_path)
            if local_backup_name in external_repo_names:
                external_repo_names.remove(local_backup_name)
            self.logger.info(
                f"> Pulling from {external_backup_path} -> {external_repo_names}"
            )

            for external_repo_name in external_repo_names:
                from_path = os.path.join(external_backup_path, external_repo_name)
                destination_path = os.path.join(root_path, external_repo_name)
                self.logger.info(f"-> Pulling from {from_path} to {destination_path}")
                self._copy(from_path, destination_path)

    def _push_local_repository(
        self,
        backup_target_path: str,
        local_backup_name: str,
        external_backup_paths: list[str],
    ) -> None:
        if len(external_backup_paths) == 0:
            self.logger.info("No remote repositories, skipping push.")
            return

        self.logger.info("> Pushing local repo to remote repos...")
        for external_backup_path in external_backup_paths:
            if not Utils.has_server_connection(external_backup_path):
                self.logger.error(
                    f"Could not establish connection to: '{external_backup_path}'"
                )
                continue

            from_path = backup_target_path
            destination_path = os.path.join(external_backup_path, local_backup_name)
            self.logger.info(f"-> Pushing from {from_path} to {destination_path}")
            self._copy(from_path, destination_path)

    def _get_repositories_from_root(self, path: str) -> list[str]:
        if ":" in path and not path.startswith("/"):
            host, remote_path = path.split(":", 1)
            cmd = ["ssh", host, f'ls -d {remote_path.rstrip("/") + "/*/"}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return [
                os.path.basename(line.rstrip("/"))
                for line in result.stdout.strip().split("\n")
                if line
            ]
        else:
            return [
                name
                for name in os.listdir(path)
                if os.path.isdir(os.path.join(path, name))
            ]

    def _copy(self, from_path: str, destination_path: str) -> None:
        subprocess.run(
            ["rsync", "-arzP", "--delete", f"{from_path}/", destination_path],
            check=True,
        )
