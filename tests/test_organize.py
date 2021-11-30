import unittest
from pathlib import Path
from ebooks.organize import crawl, Info, organize
from tempfile import TemporaryDirectory
import shutil


class TestOrganize(unittest.TestCase):
    def test_crawl(self):
        files = list(crawl(Path('./data')))
        self.assertEqual(len(files), 3)

    def test_read_epub(self):
        file = Path('./data/Septimus Heap/Magyk - Angie Sage.epub')
        info = Info.from_epub(file)
        self.assertEqual('Magyk', info.title)
        self.assertEqual('Angie Sage', info.author)

    def test_read_mobi(self):
        file = Path('./data/Storm Savage - Perfect Strangers 01 Blaze of Fury.mobi')
        info = Info.from_mobi(file)
        self.assertEqual('Away From the Sun', info.title)
        self.assertEqual('Austina Love', info.author)

    def test_organize_logic(self):
        with TemporaryDirectory() as src, TemporaryDirectory() as dest:
            shutil.copy2('./data/Angie Sage - The Magykal Papers.epub', src)
            organize(Path(src), Path(dest))
            self.assertTrue((Path(dest) / 'Angie Sage' / 'The Magykal Papers.epub').exists())
            self.assertEqual(0, len(list(Path(src).glob('*'))))


if __name__ == '__main__':
    unittest.main()
