# Batchup

Utility tool made in Python to simplify batch backup on multiple machines.

## Installation

The tool uses these cli tools to perform backups: `restic` and `rsync`.
Tested on `python 3.10.6`

```sh
git clone https://github.com/ruedoux/batchup.git
cd batchup
pip install .
```

## Usage

```sh
# Performs a local backup based on config.json
batchup backup

# Pulls remote repositories to local backup
batchup pull

# Pushes local repositories to remote backup
batchup psuh

# (Experimental) Runs "batchup backup" on remote targets
batchup remote
```

Example config.json:

```json
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
```
