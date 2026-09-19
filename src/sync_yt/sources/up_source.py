import logging as log
from yt_dlp import YoutubeDL
from yt_dlp.networking.impersonate import ImpersonateTarget
from ..domain import Item, Playlist


class UpstreamSource:
    def __init__(self, config):
        self.yt_dlp_args = {
            "extract_flat": "in_playlist",
            "quiet": True,
            "noprogress": True,
            "no_warnings": True,
            "warn_when_outdated": True,
            "js_runtimes": {"node": {}},
            "impersonate": ImpersonateTarget(client="chrome"),
        }

        if cfb := config.get("cookies_from_browser"):
            self.yt_dlp_args["cookiesfrombrowser"] = (cfb,)

    def get(self, playlist: Playlist) -> set[Item]:
        with YoutubeDL(self.yt_dlp_args) as ydl:
            try:
                info = ydl.extract_info(playlist.url, download=False)
            except Exception as e:
                raise RuntimeError("Error occured while fetching playlist info.") from e

        items = set()
        for entry in info.get("entries") or []:
            item = Item(entry["id"], entry["title"])
            if entry["duration"] is None:
                log.warning("Unavailable item detected: [%s]: %r", item.id, item.name)
            items.add(item)

        return items
