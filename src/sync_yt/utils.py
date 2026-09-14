from urllib.parse import urlparse, parse_qs


def truncate(value, max_length):
    if len(value) <= max_length:
        return value
    return value[: max_length - 3] + "..."


def get_playlist_id(url: str) -> str | None:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get("list", [None])[0]
