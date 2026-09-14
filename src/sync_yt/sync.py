import logging as log
from pathlib import Path
from .utils import truncate
from .domain import Playlist
from .db import init_database
from .sources import UpstreamSource, LocalSource, DatabaseSource


class SyncYT:
    def __init__(self, config):
        conn = init_database(Path(config["sync_dir"]).expanduser() / "sync_yt.db")
        self.config = config
        self.l_src = LocalSource(config)
        self.d_src = DatabaseSource(conn)
        self.u_src = UpstreamSource(config)

    def sync_playlist(self, playlist: Playlist):
        log.info("Syncing: %r", playlist.name)

        local_items = self.l_src.get(playlist)
        db_items = self.d_src.get(playlist)
        upstream_items = self.u_src.get(playlist)

        local_new = local_items - db_items
        local_del = db_items - local_items

        upstream_new = upstream_items - db_items
        upstream_del = db_items - upstream_items

        to_download = (local_del - upstream_del) | (upstream_new - local_new)
        to_delete = upstream_del - local_del

        actually_downloaded = self.l_src.add(playlist, to_download)
        self.d_src.add(playlist, upstream_new & (actually_downloaded | local_items))

        actually_deleted = self.l_src.remove(playlist, to_delete)
        self.d_src.remove(playlist, upstream_del & (actually_deleted | local_del))

        untracked = local_new - upstream_new
        if untracked:
            log.warning("Untracked item(s) detected:")
            for i, item in enumerate(untracked, start=1):
                log.warning(
                    "(%d/%d): [%s]: %r",
                    i,
                    len(untracked),
                    item.id,
                    truncate(item.name, 50),
                )

        if not to_download and not to_delete:
            log.info("%r is up to date.", playlist.name)
        else:
            log.info("Synced: %r", playlist.name)

    def sync_all(self):
        for playlist in self.config.get("playlists") or []:
            if not (name := playlist.get("name")):
                log.error("Playlist name is missing. Skipping playlist.")
                continue

            if not (url := playlist.get("url")):
                log.error("Playlist URL is missing for %r. Skipping playlist.", name)
                continue

            self.sync_playlist(Playlist(name, url, playlist.get("format")))
        log.info("Finished Syncing")


# U: Upstream
# L: Local
# D: DB

# Locally Added     = L - D
# Locally Removed   = D - L
# Upstream Added    = U - D
# Upstream Removed  = D - U

# local_add = (LR - UR) | (UA - LA)
# local_del = UR - LR
# db_insert = UA
# db_delete = UR
# untracked = LA - UA
