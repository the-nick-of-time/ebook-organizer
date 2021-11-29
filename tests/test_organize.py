import unittest
from pathlib import Path
from ebooks.organize import crawl, Info


class TestOrganize(unittest.TestCase):
    def test_crawl(self):
        files = list(crawl(Path('./data')))
        self.assertEqual(len(files), 8)

    def test_read_epub(self):
        file = Path('./data/Angie Sage - The Magykal Papers.epub')
        info = Info.from_epub(file)
        self.assertEqual(info.title, 'The Magykal Papers')
        self.assertEqual(info.author, 'Angie Sage')


if __name__ == '__main__':
    unittest.main()
