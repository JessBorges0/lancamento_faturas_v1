import PyPDF2
import subprocess
from typing import Tuple, Optional

# #class PdfExtraction:

#     def __init__(self):
#         pass

def is_pdf_image(pdf_path: str) -> bool:
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            for page in pdf_reader.pages:
                if page.extract_text().strip():
                    return False
        return True
    except Exception:
        return False

def ocr_pdf(input_pdf: str, output_pdf: str) -> Tuple[bool, Optional[str]]:
    """
    Applies OCR to a PDF file using OCRmyPDF.

    Args:
        input_pdf (str): Path to the input PDF file.
        output_pdf (str): Path to the output PDF file with OCR applied.

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If there is an error during the OCR process.
    """
    try:
        # Call OCRmyPDF via subprocess
        subprocess.run(['ocrmypdf', input_pdf, output_pdf], check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        if e.returncode == 10:
            return True, None
        return False, str(e)

def extract_text_from_pdf(pdf_path: str) -> Tuple[Optional[str], Optional[str]]:
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            for page in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page].extract_text()
        
        return text, None
    except Exception as e:
        return None, e
    
def invoice_type(pdf_text: str) -> Tuple[Optional[str], Optional[str]]:
    invoices = {
        "claro_telecom": ["Claro","S/A","DOCUMENTO","FINANCEIRO","N°","NOTA","FISCAL","DE","SERVICOS","DE","TELECOMUNICACOES","N°"]
    }

    for model, key_words in invoices.items():
        if all(word in pdf_text for word in key_words):
            return model, None
    return None, "No model found"