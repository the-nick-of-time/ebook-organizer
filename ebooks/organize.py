import logging
import shutil
import sys
from collections import namedtuple
from pathlib import Path
from typing import Iterable

import epub_meta
import pdfrw

from ebooks.mobi import Mobi


class Info(namedtuple('Info', ['title', 'author'])):
    EXTENSIONS = ('epub', 'mobi', 'pdf')

    @classmethod
    def from_file(cls, file: Path) -> 'Info':
        choices = {
            '.pdf': cls.from_pdf,
            '.epub': cls.from_epub,
            '.mobi': cls.from_mobi,
        }
        return choices[file.suffix](file)

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

    @classmethod
    def from_pdf(cls, file: Path) -> 'Info':
        meta = pdfrw.PdfReader(file)
        return cls((meta.Info.Title or '').strip('()'), (meta.Info.Author or '').strip('()'))


def crawl(start: Path) -> Iterable[Path]:
    for ext in Info.EXTENSIONS:
        yield from start.rglob(f"*.{ext}")


def ntfs_sanitize(name: str):
    illegal = {
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
    }
    illegal.update({chr(i): f'{i:#02x}' for i in range(0x20)})
    table = str.maketrans(illegal)
    # Remove bad characters then truncate, not guaranteed to be short enough
    # since it's just one path component
    return name.translate(table)[:100]


def modtime(f: Path) -> float:
    return max(f.stat().st_mtime, f.stat().st_ctime)


def organize(source: Path, destination: Path):
    for file in crawl(source):
        if not file.is_file():
            logging.debug("%s isn't a file, skipping", file)
            continue
        try:
            meta = Info.from_file(file)
        except Exception as e:
            logging.error('%s is unreadable as its stated type', file, exc_info=e)
            continue
        if not meta.author or not meta.title:
            logging.warning('Metadata for %s missing (%s -- %s), doing nothing', file,
                            meta.author, meta.title)
            continue
        directory = destination / ntfs_sanitize(meta.author)
        directory.mkdir(parents=True, exist_ok=True)
        new = directory / (ntfs_sanitize(meta.title) + file.suffix)
        if new.exists():
            if new.stat().st_size == file.stat().st_size:
                logging.info('Destination file %s already exists, removing duplicate %s', new,
                             file)
                file.unlink()
                continue
            if modtime(new) > modtime(file):
                logging.info('Destination file %s modified later than source %s, deleting', new,
                             file)
                file.unlink()
                continue
            if modtime(file) > modtime(new):
                logging.info('Replacing %s with newer copy %s', new, file)
                # go on to the move logic
            else:
                logging.warning('Destination file %s is not identical to source %s, skipping',
                                new, file)
                continue
        try:
            shutil.move(file, new)
            logging.info('Moved "%s" to "%s"', file.relative_to(source),
                         new.relative_to(destination))
        except OSError as e:
            logging.error("Failed to move %s to %s", file, new, exc_info=e)


if __name__ == '__main__':
    assert len(sys.argv) == 3
    src = Path(sys.argv[1])
    dest = Path(sys.argv[2])
    logging.getLogger().setLevel(logging.DEBUG)
    log = logging.FileHandler(dest / 'organize.log')
    log.setLevel(logging.INFO)
    stdout = logging.StreamHandler()
    stdout.setLevel(logging.WARNING)
    logging.basicConfig(handlers=(log, stdout))
    organize(src, dest)
