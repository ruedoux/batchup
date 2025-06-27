import subprocess


class Utils:

    @staticmethod
    def check_ssh_connection(remote_server: str) -> bool:
        try:
            subprocess.run(["ssh", remote_server, "echo"], check=True)
            return True
        except:
            return False

    @staticmethod
    def get_server_from_path(external_backup_path: str) -> str:
        path_split: list[str] = external_backup_path.split(":")
        if len(path_split) < 1:
            return f"<Failed to extract server name from: '{external_backup_path}'>"
        return path_split[0]

    @staticmethod
    def has_server_connection(external_backup_path: str) -> bool:
        remote_server = Utils.get_server_from_path(external_backup_path)
        return Utils.check_ssh_connection(remote_server)
