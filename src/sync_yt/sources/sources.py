from typing import Protocol
from ..domain import Item, Playlist


class ReadableSource(Protocol):
    def get(self, playlist: Playlist) -> set[Item]: ...


class WritableSource(ReadableSource, Protocol):
    def add(self, playlist: Playlist, items: set[Item]) -> set[Item]: ...
    def remove(self, playlist: Playlist, items: set[Item]) -> set[Item]: ...
