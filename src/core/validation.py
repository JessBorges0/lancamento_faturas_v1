import re
from unidecode import unidecode
from typing import Tuple, Optional
from controller.config import ConfigLoader

configs = ConfigLoader()

def invoice_type(text: str) -> Tuple[Optional[str], Optional[str]]:
    invoices = {
        "claro_telecom": ["Claro", "S/A", "DOCUMENTO", "FINANCEIRO", "NOTA", "FISCAL", "DE", "SERVIÇOS", "DE", "TELECOMUNICACOES"]
    }

    normalized_text = unidecode(re.sub(r'\s+', ' ', text).strip().upper())

    for model, key_words in invoices.items():
        normalized_key_words = [unidecode(word.upper()) for word in key_words]
        
        if all(word in normalized_text for word in normalized_key_words):
            return model, None

    return None, "No model found"

def validate_values(data):
    def to_float(value):
        return float(value.replace(',', '.'))

    value_total = to_float(data['valor'])

    sum = to_float(data['documento_financeiro']['valor_cobrado'][0])

    for nota in data['notas_fiscais']:
        sum += to_float(nota['valor'][0])

    if 'outros_lancamentos' in data:
        sum += to_float(data['outros_lancamentos']['valor'][0])
    
    sum = round(sum, 2)
    value_total = round(value_total, 2)

    if sum == value_total:
        return True, value_total
    return False, value_total

def extract_barcode(text: str) -> Tuple[Optional[str], Optional[str]]:
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

def check_codemp(cnpj: str) -> Tuple[Optional[dict], Optional[str]]:
    if len(cnpj) != 14:
        return None, 'Invalid CNPJ format.'
    
    companies = {
        '24272720000174': '16',
        '02959392000146': '29',
        '24126125000120': '32',
        '02959392000499': '33',
        '02959392000731': '34',
        '02959392000570': '35',
        '40828164000126': '37'
    }

    codemp = companies.get(cnpj, None)
    if codemp is None:
        return False, 'Company not found.'
    
    return True, codemp

def check_codprod_invoice(body: dict) -> dict:
    products = []
    for service in body["documento_financeiro"]["descricao"]:
        if "Juros" in service:
            products.append(250215)
        products.append(18325)
    body["documento_financeiro"]["products"] = products
    return body

def clear_cnpj(cnpj):
    formatted_standard = re.sub(r'[./-]', '', str(cnpj))
    formatted_cnpj = formatted_standard.zfill(len(str(cnpj))-4)
    
    if formatted_cnpj == '0' or not formatted_cnpj.isdigit():
        return False
    else:
        return formatted_cnpj

def conversation_values(value):
    formatted_value = value.replace('.', '').replace(',', '.') 
    return float(formatted_value)

def encode_illegal_xml_chars(data):
    return ''.join(f'&#x{ord(c):02X};' if ord(c) < 32 or ord(c) == 127 else c for c in data)