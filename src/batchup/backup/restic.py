import os
import subprocess
from batchup.logger import SimpleLogger


class Restic:

    def __init__(self, logger: SimpleLogger) -> None:
        self.logger = logger

    def backup_repository(
        self,
        backup_target_path: str,
        include_file_path: str,
        exclude_file_path: str,
        password: str,
    ) -> bool:
        if not self._verify_restic_repo(backup_target_path, password):
            self.logger.error("No restic repo found and not created.")
            return False
        if not self._verify_password(backup_target_path, password):
            self.logger.error("Restic password is wrong.")
            return False

        os.environ["RESTIC_PASSWORD"] = password
        try:
            self.logger.info(f"Backup to local repository: {backup_target_path}")
            subprocess.run(
                [
                    "restic",
                    "-r",
                    backup_target_path,
                    "backup",
                    "--files-from",
                    include_file_path,
                    "--iexclude-file",
                    exclude_file_path,
                    "--tag",
                    "main",
                    "--compression",
                    "max",
                ],
                check=True,
            )
            self.logger.info(f"Prune old snapshots: {backup_target_path}")
            subprocess.run(
                [
                    "restic",
                    "-r",
                    backup_target_path,
                    "forget",
                    "--keep-within-daily",
                    "7d",
                    "--keep-within-weekly",
                    "1m",
                    "--prune",
                ],
                check=True,
            )
            self.logger.info(f"Snapshots for {backup_target_path}:")
            subprocess.run(
                ["restic", "-r", backup_target_path, "snapshots"], check=True
            )
        finally:
            os.environ["RESTIC_PASSWORD"] = ""
        return True

    def _verify_restic_repo(self, backup_target_path: str, password: str) -> bool:
        if not os.path.isfile(os.path.join(backup_target_path, "config")):
            self.logger.warning(f"No repo detected at: {backup_target_path}")
            answer = input("Do you want to create a new repo? [Y/n] ").strip().lower()
            if answer and answer != "y":
                return False
            self._create_new_repo(backup_target_path, password)
        return True

    def _create_new_repo(self, backup_target_path: str, password: str) -> None:
        os.environ["RESTIC_PASSWORD"] = password
        try:
            result = subprocess.run(
                ["restic", "init", "--repo", backup_target_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                self.logger.error(
                    f"Failed to create restic repository at '{backup_target_path}'"
                )
                self.logger.error(result.stdout)
                self.logger.error(result.stderr)
                exit(1)
        finally:
            os.environ["RESTIC_PASSWORD"] = ""

    def _verify_password(self, backup_target_path: str, password: str) -> bool:
        os.environ["RESTIC_PASSWORD"] = password
        try:
            result = subprocess.run(
                ["restic", "-r", backup_target_path, "snapshots"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                self.logger.error(f"Wrong password for '{backup_target_path}'")
                return False
            return True
        finally:
            os.environ["RESTIC_PASSWORD"] = ""
