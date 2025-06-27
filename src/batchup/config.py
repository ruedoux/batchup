import glob
import json
import os


class Config:
    root_path: str
    local_backup_name: str
    external_backup_paths: list[str]
    includes: list[str]
    excludes: list[str]
    exclude_templates: list[str]
    matched_excludes: list[str]

    def __init__(self, config_path: str) -> None:
        with open(config_path) as f:
            json_dict = json.load(fp=f)

        self.root_path = json_dict["root-path"]
        self.local_backup_name = json_dict["local-backup-name"]
        self.external_backup_paths = json_dict.get("external-backup-paths", [])
        self.includes = json_dict.get("includes", [])
        self.excludes = json_dict.get("excludes", [])
        self.exclude_templates = json_dict.get("exclude-templates", [])

        self.matched_excludes = []
        for include_path in self.includes:
            for exclude_template in self.exclude_templates:
                matches = glob.glob(
                    pathname=exclude_template,
                    root_dir=include_path,
                    recursive=True,
                )

                for match in matches:
                    abs_match = os.path.join(include_path, match)
                    if not any(exclude in abs_match for exclude in self.excludes):
                        self.matched_excludes.append(abs_match)
