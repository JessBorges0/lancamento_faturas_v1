import unittest
import os
from tests.pdf import is_pdf_image, extract_text_from_pdf, ocr_pdf

class TestExtractor(unittest.TestCase):
    def setUp(self):
        # Define the base path for the resource files
        self.resource_path = os.path.join(os.path.dirname(__file__), 'resources')

    def test_is_pdf_image(self):
        # Test case for a PDF file containing only images
        self.assertTrue(is_pdf_image(os.path.join(self.resource_path, 'example_image.pdf')))

        # Test case for a PDF file containing text
        self.assertFalse(is_pdf_image(os.path.join(self.resource_path, 'example_text.pdf')))

    def test_ocr_pdf(self):
        # Test case for a PDF file containing only images
        result, err = ocr_pdf(os.path.join(self.resource_path, 'example_image.pdf'),os.path.join(self.resource_path, 'example_text.pdf'))
        self.assertTrue(result)
        
        # Test case for a PDF file containing text
        result, err = ocr_pdf(os.path.join(self.resource_path, 'example_text.pdf'),os.path.join(self.resource_path, 'example_image.pdf'))
        self.assertFalse(result)

    def test_extract_text_from_pdf(self):
        # Test case for successful text extraction
        text, error = extract_text_from_pdf(os.path.join(self.resource_path, 'example_text.pdf'))
        self.assertIsNotNone(text)
        self.assertIsNone(error)

        # Test case for failed text extraction
        text, error = extract_text_from_pdf('example_image.pdf')
        self.assertIsNone(text)
        self.assertIsNotNone(error)
        
        text, error = extract_text_from_pdf('nonexistent.pdf')
        self.assertIsNone(text)
        self.assertIsNotNone(error)

if __name__ == '__main__':
    unittest.main()