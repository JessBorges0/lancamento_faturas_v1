import unittest
from src.core.validation import validate_total_value, extract_barcode

class TestValidation(unittest.TestCase):
    def test_validate_total_value(self):
        # Test case for valid total value
        data = {
            "valor": "100,00",
            "documento_financeiro": {
                "valor_total": ["50,00",]
            },
            "notas_fiscais": [
                {
                    "valor_total": ["10,00", "20,00"]
                },
                {
                    "valor_total": ["5,00", "15,00"]
                }
            ]
        }
        result, error = validate_total_value(data)
        self.assertTrue(result)
        self.assertIsNone(error)

        # Test case for invalid total value
        data = {
            "valor": "100,00",
            "documento_financeiro": {
                "valor_total": ["50,00", "25,00", "25,00"]
            },
            "notas_fiscais": [
                {
                    "valor_total": ["10,00", "15,00"]
                },
                {
                    "valor_total": ["5,00", "10,00"]
                }
            ]
        }
        result, error = validate_total_value(data)
        self.assertFalse(result)
        self.assertIsNone(error)

        # Test case for missing 'valor' or 'notas_fiscais' attribute
        data = {
            "documento_financeiro": {
                "valor_total": ["50,00", "25,00", "25,00"]
            },
            "notas_fiscais": [
                {
                    "valor_total": ["10,00", "15,00"]
                },
                {
                    "valor_total": ["5,00", "20,00"]
                }
            ]
        }
        result, error = validate_total_value(data)
        self.assertFalse(result)
        self.assertEqual(error, "'valor'")

        data = {
            "valor": "100,00",
            "documento_financeiro": {
                "valor_total": ["50,00", "25,00", "25,00"]
            }
        }
        result, error = validate_total_value(data)
        self.assertFalse(result)
        self.assertEqual(error, "'notas_fiscais'")

    def test_extract_barcode(self):
        # Test case for successful barcode extraction
        barcode, error = extract_barcode('Lorem ipsum 12345678901-2 dolor sit amet 34567890123-4 Accusam aliquip accusam 56789012345-6 velit et duo amet 78901234567-8')
        self.assertEqual(barcode, '123456789012345678901234567890123456789012345678')
        self.assertIsNone(error)

        # Test case for failed barcode extraction
        barcode, error = extract_barcode('Lorem ipsum dolor sit amet')
        self.assertIsNone(barcode)
        self.assertIsNotNone(error)


if __name__ == '__main__':
    unittest.main()