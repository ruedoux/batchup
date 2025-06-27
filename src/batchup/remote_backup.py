import os
import subprocess
from batchup.logger import SimpleLogger
from batchup.config import Config
from batchup.utils import Utils
import shlex


class RemoteBackup:

    def __init__(self, logger: SimpleLogger) -> None:
        self.logger = logger

    def run(self, config: Config, password: str) -> None:
        for external_backup_path in config.external_backup_paths:
            remote_server = Utils.get_server_from_path(external_backup_path)
            if not Utils.check_ssh_connection(remote_server):
                self.logger.error(
                    f"Could not connect to remote server: '{remote_server}'"
                )
            self._backup_on_remote_server(remote_server, password)

    def _backup_on_remote_server(self, remote_server: str, password: str) -> None:
        REPO_DIR = "/tmp"
        REPO_NAME = "batchup"
        REPO_LINK = "https://github.com/ruedoux/batchup.git"
        env = os.environ.copy()
        env["RESTIC_PASSWORD"] = password

        command = shlex.quote(
            (
                f"cd {REPO_DIR} && "
                f"if [ ! -d {REPO_NAME} ]; then git clone {REPO_LINK}; fi && "
                f"cd {REPO_NAME} && "
                f"python -m venv .venv &&"
                f". .venv/bin/activate &&"
                f"pip install . &&"
                f"batchup backup -a &&"
                f"rm -rf {REPO_DIR}/{REPO_NAME}"
            )
        )
        proc = subprocess.Popen(
            ["ssh", remote_server, "bash", "-c", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )
        self.logger.info(f"Running backup on server: {remote_server}")

        for line in proc.stdout:  # pyright: ignore
            print(f"[REMOTE: {remote_server}] {line}", end="")
        for err_line in proc.stderr:  # pyright: ignore
            print(f"[REMOTE: {remote_server}] [ERR] {err_line}", end="")

        proc.wait()
        if proc.returncode != 0:
            self.logger.error(f"Backup failed on server: {remote_server}")
        if proc.returncode != 0:
            self.logger.error(f"Backup failed on server: {remote_server}")
