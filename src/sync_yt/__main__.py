import os
import sys
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
import logging as log
from pathlib import Path
from .sync import SyncYT

yaml = YAML()


def parse_config(config_path: Path):
    try:
        with open(config_path, "r") as f:
            config = yaml.load(f)
    except YAMLError as e:
        log.error("Error while parsing '%s' : %s", config_path, e)
        exit(1)
    except FileNotFoundError:
        log.error("File at '%s' does not exist.", config_path)
        exit(1)
    except Exception as e:
        log.error("An unexpected error occured: %s", e)
        exit(1)
    else:
        log.info("Using config file: '%s'", config_path)
        return config


def main():

    log.basicConfig(
        format="[sync-yt] {levelname}: {message}",
        style="{",
        level=log.INFO,
    )

    if os.name == "posix":
        config_path = Path("~/.config/sync-yt/config.yaml").expanduser()
    elif os.name == "nt":
        config_path = Path(r"~\AppData\Local\sync-yt\config.yaml").expanduser()

    if not os.path.exists(config_path):
        config_path = Path("./config.yaml")

    config = parse_config(config_path)

    sync_dir = config.get("sync_dir")

    if not sync_dir:
        log.error('"sync_dir" not defined in config')
        exit(1)

    sync_dir = Path(sync_dir).expanduser()

    if not sync_dir.exists():
        log.error("sync_dir does not exist: %s", sync_dir)
        exit(1)

    try:
        sync_yt = SyncYT(config)
    except Exception:
        sys.exit(1)

    sync_yt.sync_all()


if __name__ == "__main__":
    main()
