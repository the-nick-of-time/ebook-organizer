from pathlib import Path


def crawl(start: Path):
    for file in start.rglob("*.[em][po][ub][bi]"):
        yield file

