import unittest
from pathlib import Path
from ebooks.organize import crawl


class TestOrganize(unittest.TestCase):
    def test_crawl(self):
        files = list(crawl(Path('./data')))
        self.assertEqual(len(files), 8)


if __name__ == '__main__':
    unittest.main()
