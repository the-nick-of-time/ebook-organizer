import logging
import shutil
import sys
from collections import namedtuple
from pathlib import Path

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
        '\r': '',
        '\n': '',
        '\0': '',
        '\x0f': '',
    })
    # Remove bad characters then truncate, not guaranteed to be short enough since it's just one path component
    return name.translate(table)[:100]


def organize(source: Path, destination: Path):
    for file in crawl(source):
        if not file.is_file():
            logging.debug("%s isn't a file, skipping", file)
            continue
        if file.suffix == '.mobi':
            try:
                meta = Info.from_mobi(file)
            except Exception as e:
                logging.error('%s is unreadable as a mobi file', file, exc_info=e)
                continue
        elif file.suffix == '.epub':
            try:
                meta = Info.from_epub(file)
            except Exception as e:
                logging.error('%s is unreadable as an epub file', file, exc_info=e)
                continue
        else:
            logging.error('%s is not an epub or mobi file', file)
            continue
        if not meta.author or not meta.title:
            logging.warning('Metadata for %s missing, doing nothing', file)
            continue
        directory = destination / ntfs_sanitize(meta.author)
        directory.mkdir(parents=True, exist_ok=True)
        new = directory / (ntfs_sanitize(meta.title) + file.suffix)
        if new.exists():
            logging.warning('Destination file %s already exists, skipping on moving %s', new, file)
            continue
        shutil.move(file, new)
        logging.info('Moved "%s" to "%s"', file.relative_to(source), new.relative_to(destination))


if __name__ == '__main__':
    assert len(sys.argv) == 3
    logging.getLogger().setLevel(logging.INFO)
    src = Path(sys.argv[1])
    dest = Path(sys.argv[2])
    log = logging.FileHandler(dest / 'organize.log')
    stdout = logging.StreamHandler()
    logging.basicConfig(handlers=(log, stdout))
    organize(src, dest)
