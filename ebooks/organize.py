from pathlib import Path
from collections import namedtuple
import epub_meta


class Info(namedtuple('Info', ['title', 'author', 'series'])):
    @classmethod
    def from_epub(cls, file: Path) -> 'Info':
        data = epub_meta.get_epub_metadata(file, read_cover_image=False, read_toc=False)
        # checks for non-empty list
        author = data['authors'] and data['authors'][0]
        return cls(data['title'], author, None)


def crawl(start: Path):
    for file in start.rglob("*.[em][po][ub][bi]"):
        yield file
