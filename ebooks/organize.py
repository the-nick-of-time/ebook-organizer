from pathlib import Path
from collections import namedtuple
import shutil
import logging
import sys

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


def ntfs_sanitize(name: str):
    table = str.maketrans({
        '/': 'slash',
        '?': 'question',
        '<': 'lt',
        '>': 'gt',
        '\\': 'backslash',
        ':': '-',
        '*': 'star',
        '|': 'or',
        '"': 'quote',
    })
    return name.translate(table)


def organize(source: Path, destination: Path):
    for file in crawl(source):
        if file.suffix == '.mobi':
            meta = Info.from_mobi(file)
        elif file.suffix == '.epub':
            meta = Info.from_epub(file)
        else:
            logging.error('%s is not an epub or mobi file', file)
            continue
        if not meta.author or not meta.title:
            logging.warning('Metadata for %s missing, doing nothing', file)
            continue
        directory = destination / ntfs_sanitize(meta.author)
        directory.mkdir(parents=True, exist_ok=True)
        new = directory / (ntfs_sanitize(meta.title) + file.suffix)
        shutil.move(file, new)
        logging.info('Moved "%s" to "%s"', file, new)


if __name__ == '__main__':
    assert len(sys.argv) == 3
    logging.getLogger().setLevel(logging.INFO)
    src = Path(sys.argv[1])
    dest = Path(sys.argv[2])
    organize(src, dest)
