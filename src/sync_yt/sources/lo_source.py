import re
import logging as log
from pathlib import Path
from yt_dlp import YoutubeDL
from yt_dlp.networking.impersonate import ImpersonateTarget
from ..utils import truncate
from ..domain import Item, Playlist


class LocalSource:

    def __init__(self, config):
        self.config = config
        self.yt_dlp_args = {
            "ignoreerrors": "only_download",
            "quiet": True,
            "js_runtimes": {"node": {}},
            "warn_when_outdated": True,
            "impersonate": ImpersonateTarget(client="chrome"),
        }

        if cfb := config.get("cookies_from_browser"):
            self.yt_dlp_args["cookiesfrombrowser"] = (cfb,)

    def get(self, playlist: Playlist) -> set[Item]:
        path = Path(self.config["sync_dir"]).expanduser() / playlist.name

        if not path.is_dir():
            return set()

        items = set()
        pattern = re.compile(r"(?P<name>.+?) \[(?P<id>[A-Za-z0-9_-]{11})\]\.[^.]+")
        for file in path.iterdir():
            if file.is_file():
                match = pattern.fullmatch(file.name)
                if match:
                    item_id = match.group("id")
                    name = match.group("name")
                    items.add(Item(item_id, name))
        return items

    def add(self, playlist: Playlist, items: set[Item]) -> set[Item]:
        path = Path(self.config["sync_dir"]).expanduser() / playlist.name

        if not path.is_dir():
            log.info("Downloading new playlist at: %r", path)
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                log.error("Error creating directory %r: %s", path, e)
                return set()

        args = self.yt_dlp_args.copy()
        args["paths"] = {"home": str(path)}
        args.update(audio_args(playlist.format))

        added_items = set()
        total = len(items)
        if items:
            log.info("%d item(s) to download", total)

        with YoutubeDL(args) as ydl:
            for i, item in enumerate(items, start=1):
                log.info(
                    "Downloading (%d/%d): [%s]: %r",
                    i,
                    total,
                    item.id,
                    truncate(item.name, 50),
                )
                try:
                    ydl.download(item.id)
                    added_items.add(item)
                except Exception as e:
                    log.error("Error occured while downloading: [%s]: %s", item.id, e)
        return added_items

    def remove(self, playlist: Playlist, items: set[Item]) -> set[Item]:
        path = Path(self.config["sync_dir"]).expanduser() / playlist.name

        removed_items = set()
        total = len(items)
        for i, item in enumerate(items, start=1):
            log.info(
                "Removing (%d/%d): [%s]: %r",
                i,
                total,
                item.id,
                truncate(item.name, 50),
            )
            removed = False
            failed = False
            for file in path.iterdir():
                if not file.is_file():
                    continue
                if f"[{item.id}]." in file.name:
                    try:
                        file.unlink()
                        removed = True
                    except OSError as e:
                        log.error("Error occured while removing: [%s]: %s", item.id, e)
                        failed = True
                        break
            if not failed:
                removed_items.add(item)
                if not removed:
                    log.warning("Item already removed: [%s]", item.id)

        return removed_items


def audio_args(codec: str | None) -> dict:

    preferred_codec = codec or "best"

    postprocessors = [
        {
            "key": "FFmpegExtractAudio",
            "nopostoverwrites": False,
            "preferredcodec": preferred_codec,
            "preferredquality": "0",
        }
    ]

    args = {
        "format": "bestaudio/best",
        "postprocessors": postprocessors,
    }

    if codec != "best":
        args["final_ext"]: codec

    # Embed metadata if compatible format
    if preferred_codec in {"mp3", "m4a", "flac", "opus", "ogg"}:
        postprocessors.append(
            {
                "key": "FFmpegMetadata",
                "add_chapters": False,
                "add_infojson": False,
                "add_metadata": True,
            }
        )

    # Embed thumbnail as a cover art if compatible format
    if preferred_codec in {"mp3", "m4a", "flac"}:
        postprocessors.extend(
            [
                {
                    "key": "FFmpegThumbnailsConvertor",
                    "format": "jpg",
                },
                {
                    "key": "EmbedThumbnail",
                    "already_have_thumbnail": False,
                },
            ]
        )

        args["outtmpl"] = {"pl_thumbnail": ""}
        args["writethumbnail"] = True

    return args
