class Playlist:
    def __init__(self, name, url, format):
        self.name = name
        self.url = url
        self.format = format


class Item:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def values(self):
        return (self.id, self.name)
