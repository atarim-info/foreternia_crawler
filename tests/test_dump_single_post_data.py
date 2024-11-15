import json
import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import sys
import os

# Add the project root to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_extractor import extractor as extractor

output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

class TestDumpSinglePostData(unittest.TestCase):

    def setUp(self):
        html_file = 'tests/data/post-5299.html'
        
        with open("tests/data/post-5299.json", 'r', encoding='utf-8') as json_file:
            self.post_mock_data = json.load(json_file)
        
        self.post_html = self.read_file_to_string(html_file)
        self.post_soup = BeautifulSoup(self.post_html, 'html.parser')
        self.post = self.post_soup.find("div", id="post-5299")

    def read_file_to_string(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
        
    @patch('json.dump')
    @patch('os.path.join')
    def test_valid_post(self, mock_join, mock_dump):
        post_data = extractor.get_single_post_data(self.post, output_dir=output_dir)
        self.maxDiff = None
        self.assertEqual(post_data, self.post_mock_data)
        

    @patch('json.dump')
    @patch('os.path.join')
    def test_missing_post_id(self, mock_join, mock_dump):
        self.post.attrs.pop("id")
        with self.assertRaises(KeyError):
            extractor.get_single_post_data(self.post, output_dir=output_dir)

    @patch('json.dump')
    @patch('os.path.join')
    def test_missing_author_name(self, mock_join, mock_dump):
        self.post.find("div", class_="author-name").decompose()
        with self.assertRaises(AttributeError):
            extractor.get_single_post_data(self.post, output_dir=output_dir)

    @patch('json.dump')
    @patch('os.path.join')
    def test_missing_post_content(self, mock_join, mock_dump):
        self.post.find("div", class_="wpforo-post-content").decompose()
        with self.assertRaises(AttributeError):
            extractor.get_single_post_data(self.post, output_dir=output_dir)

    @patch('json.dump')
    @patch('os.path.join')
    def test_missing_content_bottom(self, mock_join, mock_dump):
        self.post.find("div", class_="wpforo-post-content-bottom").decompose()
        with self.assertRaises(AttributeError):
            extractor.get_single_post_data(self.post, output_dir=output_dir)

if __name__ == '__main__':
    unittest.main()