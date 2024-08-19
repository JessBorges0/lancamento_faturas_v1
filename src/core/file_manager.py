import os
import re
import shutil
import PyPDF2
import subprocess
from typing import Tuple, Optional
from controller.config import ConfigLoader
from pdfminer.high_level import extract_text

class FileManager:

    def __init__(self, logger):
        self.logger = logger
        self.configs = ConfigLoader()
        self.destination_folder = os.path.join(os.getcwd(), 'src\\data\\download_file_ocr')

    def check_password_pdf(self, pdf_path):
        try:
            pdf_file = open(pdf_path, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            is_protected = pdf_reader.is_encrypted
            pdf_file.close()
            if is_protected:
                self.logger.info("PDF com proteção de senha")
                return is_protected
            else:
                self.logger.info("PDF sem proteção de senha")
                return is_protected
        except Exception as e:
            self.logger.info(f"Ocorreu um erro: {str(e)}")
            return False

    def is_pdf_image(self, pdf_path: str) -> bool:
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                for page in pdf_reader.pages:
                    if page.extract_text().strip():
                        return False
            return True
        except Exception:
            return False
        
    def ocr_pdf(self, input_pdf: str, output_pdf: str) -> Tuple[bool, Optional[str]]:
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
            subprocess.run(['ocrmypdf', input_pdf, output_pdf], check=True)
            return True, None
        except subprocess.CalledProcessError as e:
            if e.returncode == 10:
                return True, None
            return False, str(e)

    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            text = extract_text(pdf_path)
            if text:
                return text, None
            else:
                return None, "Texto não encontrado ou PDF vazio"
        except Exception as e:
            self.logger.error(f"Erro ao extrair texto de {pdf_path} com pdfminer: {str(e)}")
            return None, str(e)
        
    def extract_barcode(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        regex = r'\d{11}-\d{1}\b'
        try:
            barcode_matches = re.findall(regex, text)
            first_four_matches = barcode_matches[:4]
            concatenated_code = ''.join(first_four_matches).replace('-', '')
            if concatenated_code:
                return concatenated_code, None
            else:
                return None, 'No barcode found in the text.'
        except Exception as e:
            return None, e
        
    def copy_attachment(self, **kwargs):
        self.pasta_chamado = os.path.join(self.destination_folder, 
                                        str(kwargs["chamado"]))

        if not os.path.exists(self.pasta_chamado):
            os.makedirs(self.pasta_chamado)

        if os.path.exists(kwargs["caminho_servidor"]):
            self.caminho_destino = os.path.join(self.pasta_chamado, kwargs["chamado"] + kwargs["formato"])
            try:
                shutil.copy(kwargs["caminho_servidor"], self.caminho_destino)
                self.logger.info(f"Arquivo de '{kwargs['caminho_servidor']}' copiado como '{self.caminho_destino}'")
                return True

            except Exception as e:
                self.logger.error(f"Erro ao copiar arquivo: {e}")
                return False
                
        else:
            self.logger.error(f"Arquivo '{kwargs['caminho_servidor']}' não encontrado")
            return False
        
    def result_calls_executed(self):
        try:
            with open('src\\data\\base_calls_executed.txt', 'r') as f:
                list = [line.strip() for line in f.readlines()]
                calls_str = ', '.join(map(str, list))
                return True, calls_str
        except Exception as e:
            return False, f"Um erro ocorreu: {e}"
    
    def save_calls_executed(self, calls):
        try:
            with open('src\\data\\base_calls_executed.txt', 'a') as f:
                f.write('\n')
                f.write('\n'.join(calls))
            return True
        except Exception as e:
            return False
    
    def result_str_calls_sql(self, list_calls):
        calls = ', '.join(str(calls) for calls in list_calls)
        return calls