from pathlib import Path
from collections import namedtuple
import shutil
import logging

import epub_meta
from ebooks.mobi import Mobi


class Info(namedtuple('Info', ['title', 'author'])):
    @classmethod
    def from_epub(cls, file: Path) -> 'Info':
        data = epub_meta.get_epub_metadata(file, read_cover_image=False, read_toc=False)
        # checks for non-empty list
        author = data['authors'] and data['authors'][0]
        return cls(data['title'], author)

    @classmethod
    def from_mobi(cls, file: Path) -> 'Info':
        meta = Mobi(str(file))
        return cls(meta.title().decode('utf-8'), meta.author().decode('utf-8'))


def crawl(start: Path):
    for file in start.rglob("*.[em][po][ub][bi]"):
        yield file


def organize(source: Path, destination: Path):
    for file in crawl(source):
        if file.suffix == '.mobi':
            meta = Info.from_mobi(file)
        elif file.suffix == '.epub':
            meta = Info.from_epub(file)
        else:
            logging.getLogger().error('%s is not an epub or mobi file', file)
            continue
        if not meta.author or not meta.title:
            logging.getLogger().error('Metadata for %s missing', file)
            continue
        directory = destination / meta.author
        directory.mkdir(parents=True, exist_ok=True)
        new = directory / (meta.title + file.suffix)
        shutil.move(file, new)
