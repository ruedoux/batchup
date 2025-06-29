import os
from batchup.logger import SimpleLogger
from batchup.config import Config
from batchup.utils import Utils


class RemoteBackup:

    def __init__(self, logger: SimpleLogger) -> None:
        self.logger = logger

    def run(self, config: Config) -> None:
        for external_backup_path in config.remote_backup_paths:
            remote_server = Utils.get_server_from_path(external_backup_path)
            if not Utils.check_ssh_connection(remote_server):
                self.logger.error(
                    f"Could not connect to remote server: '{remote_server}'"
                )
            self._backup_on_remote_server(remote_server)

    def _backup_on_remote_server(self, remote_server: str) -> None:
        REPO_DIR = "/tmp"
        REPO_NAME = "batchup"
        REPO_LINK = "https://github.com/ruedoux/batchup.git"
        command = (
            f"cd {REPO_DIR} && "
            f"[ ! -d {REPO_NAME} ] && git clone {REPO_LINK} || true && "
            f"cd {REPO_NAME} && "
            f"git fetch && git pull && "
            f"[ ! -d .venv ] && python -m venv .venv || true && "
            f". .venv/bin/activate && "
            f"pip install . && "
            f"batchup backup"
        )

        self.logger.info("-" * 16)
        self.logger.info(f"Running backup on server: {remote_server}")
        self.logger.info("-" * 16)
        return_code = os.system(f'ssh -t {remote_server} "bash -c \\"{command}\\""')
        if return_code != 0:
            self.logger.error(f"Backup failed on server: {remote_server}")
        self.logger.info("-" * 16)
        self.logger.info(f"Finished backup on server: {remote_server}")
        self.logger.info("-" * 16)
