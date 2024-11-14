import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import json
import os

from ..src.data_extractor import extractor as extractor

class TestGetSinglePostData(unittest.TestCase):

    def setUp(self):
        self.post_html = """
        <div id="post-123">
            <div class="author-name">John Doe</div>
            <div class="wpforo-post-content">This is the post content.</div>
            <div class="wpforo-post-content-bottom">This is the content bottom.</div>
        </div>
        """
        self.post_soup = BeautifulSoup(self.post_html, 'html.parser')
        self.post = self.post_soup.find("div", id="post-123")

    @patch('json.dump')
    @patch('os.path.join')
    def test_valid_post(self, mock_join, mock_dump):
        mock_join.return_value = "output_dir/post-123.json"
        extractor.get_single_post_data(self.post)
        mock_dump.assert_called_once_with({"id": "post-123", "author": "John Doe", "content": "This is the post content.", "content_bottom": "This is the content bottom."}, mock_join.return_value, indent=2)

    @patch('json.dump')
    @patch('os.path.join')
    def test_missing_post_id(self, mock_join, mock_dump):
        self.post.attrs.pop("id")
        with self.assertRaises(KeyError):
            extractor.get_single_post_data(self.post)

    @patch('json.dump')
    @patch('os.path.join')
    def test_missing_author_name(self, mock_join, mock_dump):
        self.post.find("div", class_="author-name").decompose()
        with self.assertRaises(AttributeError):
            extractor.get_single_post_data(self.post)

    @patch('json.dump')
    @patch('os.path.join')
    def test_missing_post_content(self, mock_join, mock_dump):
        self.post.find("div", class_="wpforo-post-content").decompose()
        with self.assertRaises(AttributeError):
            extractor.get_single_post_data(self.post)

    @patch('json.dump')
    @patch('os.path.join')
    def test_missing_content_bottom(self, mock_join, mock_dump):
        self.post.find("div", class_="wpforo-post-content-bottom").decompose()
        extractor.get_single_post_data(self.post)
        mock_dump.assert_called_once_with({"id": "post-123", "author": "John Doe", "content": "This is the post content.", "content_bottom": ""}, mock_join.return_value, indent=2)

if __name__ == '__main__':
    unittest.main()