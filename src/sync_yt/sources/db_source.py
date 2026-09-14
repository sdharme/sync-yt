from ..domain import Item, Playlist
from ..utils import get_playlist_id


class DatabaseSource:

    def __init__(self, connection):
        self.connection = connection

    def get(self, playlist: Playlist) -> set[Item]:
        pl_id = get_playlist_id(playlist.url)
        items = self.connection.execute(
            """
                SELECT i.*
                FROM items AS i
                JOIN playlist_items AS pi
                    ON pi.item_id = i.id
                WHERE pi.playlist_id = ?
            """,
            (pl_id,),
        )
        return {Item(i[0], i[1]) for i in items}

    def add(self, playlist: Playlist, items: set[Item]) -> set[Item]:
        pl_id = get_playlist_id(playlist.url)
        with self.connection:
            self.connection.execute(
                """
                    INSERT OR IGNORE INTO playlists (id, name)
                    VALUES (?, ?)
                """,
                (pl_id, playlist.name),
            )

            self.connection.executemany(
                """
                    INSERT OR IGNORE INTO items (id, name)
                    VALUES (?, ?)
                """,
                (item.values() for item in items),
            )

            self.connection.executemany(
                """
                    INSERT OR IGNORE INTO playlist_items (playlist_id, item_id)
                    VALUES (?, ?)
                """,
                ((pl_id, item.id) for item in items),
            )
        return items

    def remove(self, playlist: Playlist, items: set[Item]) -> set[Item]:
        pl_id = get_playlist_id(playlist.url)
        with self.connection:
            self.connection.executemany(
                """
                    DELETE FROM playlist_items
                    WHERE playlist_id = ?
                    AND item_id = ?
                """,
                ((pl_id, item.id) for item in items),
            )

            self.connection.executemany(
                """
                    DELETE FROM items
                    WHERE id = ?
                    AND NOT EXISTS (
                        SELECT 1
                        FROM playlist_items
                        WHERE playlist_items.item_id = items.id
                    )
                """,
                ((item.id,) for item in items),
            )
        return items
