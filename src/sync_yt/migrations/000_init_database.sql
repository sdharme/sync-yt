CREATE TABLE items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE playlists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE playlist_items (
    playlist_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    PRIMARY KEY (playlist_id, item_id),
    FOREIGN KEY (playlist_id)
        REFERENCES playlists(id)
        ON DELETE CASCADE,
    FOREIGN KEY (item_id)
        REFERENCES items(id)
        ON DELETE CASCADE
);
