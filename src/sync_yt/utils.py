from urllib.parse import urlparse, parse_qs
import json
import urllib.request
import urllib.error


def truncate(value, max_length):
    if len(value) <= max_length:
        return value
    return value[: max_length - 3] + "..."


def get_playlist_id(url: str) -> str | None:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get("list", [None])[0]


def get_latest_ytdlp_version():
    url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "yt-dlp-version-check",
        },
    )

    with urllib.request.urlopen(request, timeout=5) as response:
        data = json.load(response)

    return data["tag_name"].lstrip("v")
