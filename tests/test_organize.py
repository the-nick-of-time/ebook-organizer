import unittest
from pathlib import Path
from ebooks.organize import crawl, Info


class TestOrganize(unittest.TestCase):
    def test_crawl(self):
        files = list(crawl(Path('./data')))
        self.assertEqual(len(files), 3)

    def test_read_epub(self):
        file = Path('./data/Septimus Heap/Magyk - Angie Sage.epub')
        info = Info.from_epub(file)
        self.assertEqual('Magyk', info.title)
        self.assertEqual('Angie Sage', info.author)


if __name__ == '__main__':
    unittest.main()
