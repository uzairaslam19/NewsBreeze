import unittest
import tempfile
import os
import json
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cgi")
from unittest.mock import patch, MagicMock
from Scrapy_Project.scrapenews.spiders.new_spider import News_Spider
from project import (
    main,
    scrape,
    load_scraped_news,
    clean_text,
    summarise,
    get_summaries_callback, 
    get_news_callback
)

class TestScript(unittest.TestCase):


    @patch('project.dpg.get_value')
    @patch('project.dpg.set_value')
    @patch('project.clean_text')
    @patch('project.summarise')
    def test_get_summaries_callback(self, mock_summarise, mock_clean_text, mock_set_value, mock_get_value):
        # Set up mock objects and values
        mock_get_value.return_value = True  # Simulate "Summary_Input" checked
        mock_summarise.return_value = ["1: Summary 1", "2: Summary 2"]

        # Mock Hydra configuration
        cfg = MagicMock()

        # Call the get_summaries_callback function
        get_summaries_callback(cfg, sender=None, sum=True)

        # Assertions
        #mock_set_value.assert_called_with("news_text", "Now Summarizing your news, Please Wait!!")
        mock_clean_text.assert_called_with(cfg)
        mock_summarise.assert_called_with(cfg)
        mock_set_value.assert_called_with("news_text", "\n1:\n Summary 1\n\n2:\n Summary 2\n")
        


    def test_load_scraped_news(self):
        # Create a temporary JSON file with some data
        data = [{"title": "Test Article 1", "author": "Author 1"}]
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
            json.dump(data, temp_file)
            temp_file_path = temp_file.name
        
        # Test the load_scraped_news function
        scraped_data = load_scraped_news(temp_file_path)
        
        self.assertEqual(len(scraped_data), 1)
        self.assertEqual(scraped_data[0]['title'], 'Test Article 1')
        self.assertEqual(scraped_data[0]['author'], 'Author 1')

        # Clean up the temporary file
        os.remove(temp_file_path)

    def test_clean_text(self):
        # Test the clean_text function
        # Mock Hydra configuration for testing
        class MockHydraConfig:
            def __init__(self):
                self.path = MockPathConfig()

        class MockPathConfig:
            def __init__(self):
                self.json_output = "mock_json_output.json"
                self.cleaned_json_output = "mock_cleaned_json_output.json"

        # Create a temporary JSON file with some data
        data = [{"title": "Test Article 1", "content": "Article content 1"}]
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
            json.dump(data, temp_file)
            temp_file_path = temp_file.name

        # Mock the Clean_News module and function
        with patch('project.Clean_News') as MockCleanNews:
            mock_clean_news_instance = MockCleanNews.return_value
            mock_clean_news_instance.news_list.return_value = None

            # Create a mock Hydra configuration object
            mock_cfg = MockHydraConfig()

            # Test the clean_text function by passing the mock cfg
            clean_text(mock_cfg)

        # Clean up the temporary file
        os.remove(temp_file_path)




if __name__ == '__main__':
    unittest.main()