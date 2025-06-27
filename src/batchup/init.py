import os
import shutil

from batchup.logger import SimpleLogger


class Init:
    _EXAMPLE_CONFIGURATION = """
{
  "root-path": "/mnt/backup/bck",
  "local-backup-name": "pc",
  "external-backup-paths": ["myserver:/mnt/backup/bck"],
  "includes": ["/home/name/files"],
  "excludes": ["/home/name/files/videos"],
  "exclude-templates": [
    "**/.git",
    "**/bin",
    "**/obj",
    "**/build",
    "**/*.egg-info",
    "**/__pycache__",
    "**/*.exe"
  ]
}
    """

    def __init__(self, logger: SimpleLogger) -> None:
        self.logger = logger

    def check_requirements(self) -> None:
        REQUIRED_COMMANDS = ["restic", "rsync"]

        for command in REQUIRED_COMMANDS:
            if not shutil.which(command):
                self.logger.error(f"The tool requires '{command}' to be installed")
                exit(1)

    def prepare_config(self) -> None:
        home_dir = os.path.expanduser("~")
        dir_path = os.path.join(home_dir, ".config", "batchup")
        default_config_path = os.path.join(dir_path, "config.json")

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            self.logger.info(
                f"Did not detect configuration folder, creating one at '{dir_path}'"
            )

            with open(default_config_path, "w") as f:
                f.write(self._EXAMPLE_CONFIGURATION)
            self.logger.info(
                f"Created default configuration, please change it before running: {default_config_path}'"
            )
            exit()
