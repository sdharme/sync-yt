# sync-yt

**sync-yt** is a command-line tool that keeps YouTube Music playlists mirrored to local
directories on your system. It downloads tracks with [yt-dlp](https://github.com/yt-dlp/yt-dlp),
tags them, and tracks sync state in a local SQLite database so that changes made upstream
*and* changes you make locally are both handled correctly.

> **Note:** As of v2.0.0, sync-yt is an audio-only tool. Video playlist syncing was removed
> in favour of becoming a focused music library manager. If you need video downloads, use
> `yt-dlp` directly or stay on v1.x.

## Features

+ Declarative `config.yaml` to specify playlists and options.
+ Three-way sync between YouTube, your local folder, and a state database.
+ Embeds metadata and cover art into audio files when the codec supports it.
+ Can sync private playlists by pulling cookies from your logged-in browser.
+ Detects tracks that have become unavailable upstream.
+ Automatically skips duplicate entries within a playlist.

## Requirements

+ Python 3.10+
+ [Node.js](https://nodejs.org/en/download)
+ [FFmpeg](https://ffmpeg.org/download.html)

Make sure both Node.js and FFmpeg are in your `PATH`.

FFmpeg is **required** in v2.x, since every download is passed through audio extraction.
Node.js is used by yt-dlp for JavaScript challenge solving.

## Installation

+ ### Windows
  ```
  $ pip install sync-yt
  ```

+ ### Arch Linux
  `sync-yt` is available on the [AUR](https://aur.archlinux.org/packages/sync-yt).
  Use your favourite AUR helper.
  ```
  $ yay -S sync-yt
  ```

+ ### Other Linux Distributions / macOS
  Since `sync-yt` requires a latest version of `yt-dlp`, which may not be available in your
  OS's official repositories, using `pipx` is recommended.

  ```
  $ pipx ensurepath
  $ pipx install sync-yt
  ```

## Configuration

The configuration file is searched for in this order:

1. `~/.config/sync-yt/config.yaml` on POSIX systems, or
   `C:\Users\<User>\AppData\Local\sync-yt\config.yaml` on Windows.
2. `./config.yaml` in the current working directory.

If neither exists, sync-yt exits with an error.

### `sync_dir`

+ **Type:** `string`: **required**
+ **Description:** The local directory where playlist folders are created. May be an
  absolute path or use `~` for your home directory. The directory must already exist;
  sync-yt will not create it for you.
+ **Examples:** `~/Music`, `D:\Music`

### `cookies_from_browser`

+ **Type:** `string`: optional
+ **Description:** The browser to extract cookies from. Required for playlists that are only
  accessible while signed into a Google account. Omit it if you only sync public playlists.
+ **Examples:** `firefox`, `chrome`, `brave`, `edge`, `vivaldi`

### `playlists`

+ **Type:** `list`:  a list of playlist entries, each with the following keys:

  + **`name`**: *required*
    + **Type:** `string`
    + **Description:** A name for the playlist. This is also the name of the folder created
      inside `sync_dir` where the playlist is synced. A playlist with a missing `name`
      is skipped with an error.

  + **`url`**: *required*
    + **Type:** `string`
    + **Description:** The URL of the YouTube playlist. Must contain a `list=` query
      parameter, which is used as the playlist's identity in the state database. A playlist
      with a missing `url` is skipped with an error.
    + **Example:** `https://www.youtube.com/playlist?list=PLSdoVPM5WnndSQEXRz704yQkKwx76GvPV`

  + **`format`**: optional
    + **Type:** `string`
    + **Description:** The audio codec to convert to. Defaults to `best`, which keeps the
      best available source audio without re-encoding.
    + **Supported values:** `best`, `aac`, `alac`, `flac`, `m4a`, `mp3`, `opus`, `vorbis`, `wav`
    + **Example:** `mp3`

### Example configuration

```yaml
sync_dir: ~/Music
cookies_from_browser: firefox

playlists:
  - name: Daft Punk - Discovery
    url: https://www.youtube.com/playlist?list=PLSdoVPM5WnndSQEXRz704yQkKwx76GvPV
    format: mp3

  # Keep source quality, no re-encode
  - name: Liked Songs
    url: https://www.youtube.com/playlist?list=LM
```

## Usage

```
$ sync-yt
```

Every playlist in the config is synced in order. Progress, warnings, and errors are written
to the console.

## How syncing works

sync-yt compares three sources on every run:

+ **Upstream**: the current contents of the YouTube playlist.
+ **Local**: the files currently present in the playlist's folder.
+ **Database**: the last known synced state, stored in `.sync_yt.db` inside `sync_dir`.

Based on this comparison, `sync-yt` downloads/removes local items to match the upstream playlist.

Downloaded files are named `<title> [<video id>].<ext>`. The video ID in the filename is how
sync-yt recognises its own files, so **renaming files will cause them to be treated as
untracked** and their tracks to be re-downloaded on the next sync.

The database is created automatically on first run and migrated forward as needed.

## Notes

+ Manual intervention is needed when a track becomes unavailable upstream. Remove it from
  the YouTube playlist to clear the warning. Once removed upstream, it is deleted locally on
  the next sync. Back up first if you want to keep the file.
+ Metadata is embedded for `mp3`, `m4a`, `flac`, `opus`, and `ogg`.
+ Cover art is embedded for `mp3`, `mka`, `m4a`, `flac`, `opus` and `ogg`.

## License

MIT see [LICENSE](LICENSE).
