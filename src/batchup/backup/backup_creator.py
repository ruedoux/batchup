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
        local_backup_path: str,
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

        self._check_repository_directory(local_backup_path)
        backup_target_path = os.path.join(local_backup_path, local_backup_name)
        if not self.restic.backup_repository(
            backup_target_path=backup_target_path,
            include_file_path=include_file_path,
            exclude_file_path=exclude_file_path,
            password=password,
        ):
            self.logger.error("Failed to create restic backup. Aborting.")
            exit(1)

    def backup_remote(
        self,
        local_backup_path: str,
        local_backup_name: str,
        remote_backup_paths: list[str],
    ) -> None:
        self._pull_remote_repositories(
            local_backup_path, local_backup_name, remote_backup_paths
        )
        self._push_local_repositories(
            local_backup_path=local_backup_path,
            remote_backup_paths=remote_backup_paths,
        )

    def _pull_remote_repositories(
        self,
        local_backup_path: str,
        local_backup_name: str,
        remote_backup_paths: list[str],
    ) -> None:
        if len(remote_backup_paths) == 0:
            self.logger.info("No remote repositories, skipping pull.")
            return

        self._check_repository_directory(local_backup_path)
        self.logger.info(msg="Pulling remote repositories to local repository...")
        for external_backup_path in remote_backup_paths:
            if not Utils.has_server_connection(external_backup_path):
                self.logger.error(
                    f"Could not establish connection to: '{external_backup_path}'"
                )
                continue

            external_repo_names = self._get_remote_repository_names(
                external_backup_path
            )
            if local_backup_name in external_repo_names:
                external_repo_names.remove(local_backup_name)
            self.logger.info(
                f"> Pulling from {external_backup_path} -> {external_repo_names}"
            )

            for external_repo_name in external_repo_names:
                from_path = os.path.join(external_backup_path, external_repo_name)
                destination_path = os.path.join(local_backup_path, external_repo_name)
                self.logger.info(f"-> Pulling from {from_path} to {destination_path}")
                self._copy(from_path, destination_path)

    def _push_local_repositories(
        self, local_backup_path: str, remote_backup_paths: list[str]
    ) -> None:
        if len(remote_backup_paths) == 0:
            self.logger.info("No remote repositories, skipping push.")
            return

        self._check_repository_directory(local_backup_path)
        self.logger.info("> Pushing local repos to remote repos...")
        for remote_backup_path in remote_backup_paths:
            if not Utils.has_server_connection(remote_backup_path):
                self.logger.error(
                    f"Could not establish connection to: '{remote_backup_path}'"
                )
                continue

            local_repo_names = self._get_local_repository_names(local_backup_path)
            for local_repo_name in local_repo_names:
                from_path = os.path.join(local_backup_path, local_repo_name)
                destination_path = os.path.join(remote_backup_path, local_repo_name)
                self.logger.info(f"-> Pushing from {from_path} to {destination_path}")
                self._copy(from_path, destination_path)

    def _check_repository_directory(self, local_backup_path: str) -> None:
        if not os.path.exists(local_backup_path):
            self.logger.info("Did not detect root folder for repositiories.")
            self.logger.info(f"Creating folder: '{local_backup_path}'")
            os.makedirs(name=local_backup_path)

    def _get_local_repository_names(self, target_path: str) -> list[str]:
        return [
            name
            for name in os.listdir(target_path)
            if os.path.isdir(os.path.join(target_path, name))
        ]

    def _get_remote_repository_names(self, target_path: str) -> list[str]:
        host, remote_path = target_path.split(":", 1)
        cmd = ["ssh", host, f'ls -d {remote_path.rstrip("/") + "/*/"}']
        result = subprocess.run(cmd, capture_output=True, text=True)
        return [
            os.path.basename(line.rstrip("/"))
            for line in result.stdout.strip().split("\n")
            if line
        ]

    def _copy(self, from_path: str, destination_path: str) -> None:
        subprocess.run(
            ["rsync", "-arzP", "--delete", f"{from_path}/", destination_path],
            check=True,
        )
