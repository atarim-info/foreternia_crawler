import unittest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
import json
import os

# import sys
# sys.path.insert(0, '..')
# from data_extractor import extractor as extractor
import data_extractor.extractor as extractor

class TestDataExtractor(unittest.TestCase):
    def setUp(self):
        self.session = Mock()
        self.url = 'https://example.com'

    @patch('requests.get')
    def test_successful_response(self, mock_get):
        # Mock successful response with valid HTML content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '<html><body><article class="buddyx-article" id="123"><div class="post-meta-category__item">Category</div><h2>Title</h2><div class="entry-content">Post content</div></article></body></html>'
        mock_get.return_value = mock_response

        # Call the function
        extractor.get_data_from_homepage(self.session, self.url)

        # Check if the file was created with the correct data
        with open('data/123.json', 'r') as f:
            data = json.load(f)
            self.assertEqual(data, {'post_id': '123', 'category': 'Category', 'title': 'Title', 'post': 'Post content'})

    @patch('requests.get')
    def test_unsuccessful_response(self, mock_get):
        # Mock unsuccessful response (non-200 status code)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call the function
        extractor.get_data_from_homepage(self.session, self.url)

        # Check if no file was created
        self.assertFalse(os.path.exists('data/123.json'))

    @patch('requests.get')
    def test_invalid_html_content(self, mock_get):
        # Mock invalid HTML content (missing expected tags or classes)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '<html><body><article class="buddyx-article" id="123"></article></body></html>'
        mock_get.return_value = mock_response

        # Call the function
        extractor.get_data_from_homepage(self.session, self.url)

        # Check if no file was created
        self.assertFalse(os.path.exists('data/123.json'))

    @patch('requests.get')
    @patch('json.dump')
    def test_file_io_error(self, mock_dump, mock_get):
        # Mock file I/O error
        mock_dump.side_effect = IOError('Mocked file I/O error')

        # Mock successful response with valid HTML content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '<html><body><article class="buddyx-article" id="123"><div class="post-meta-category__item">Category</div><h2>Title</h2><div class="entry-content">Post content</div></article></body></html>'
        mock_get.return_value = mock_response

        # Call the function
        extractor.get_data_from_homepage(self.session, self.url)

        # Check if the file was not created
        self.assertFalse(os.path.exists('data/123.json'))

if __name__ == '__main__':
    unittest.main()