import json
from controller.openai import OpenAIController
from core.validation import extract_barcode, validate_values
from tests.pdf import ocr_pdf, extract_text_from_pdf, is_pdf_image, invoice_type

# Exemplo de uso
openai = OpenAIController()
input_file = r'tests\resources\Claro - 2097521.pdf'
output_file = r'tests\resources\Claro - 2097521_ocr.pdf'

print("Starting OCR process...")
pdf_image = is_pdf_image(input_file)
if pdf_image:
    success, err = ocr_pdf(input_file, output_file)
    if not success:
        raise Exception(f"Error: {err}")
    print("OCR process completed successfully.")

print("Extracting text from PDF...")
text, err = extract_text_from_pdf(output_file)
if err:
    raise Exception(f"Error: {err}")
print("Text extraction completed successfully.")

print("Extracting barcode from text...")
barcode, err = extract_barcode(text)
if err:
    raise Exception(f"Error: {err}")
print("Barcode extraction completed successfully.")

print(f"Checking model for invoice type...")
model, err = invoice_type(pdf_text=text)
if err:
    raise Exception(f"Error: {err}")
print(f"Model: {model}")

print("Loading prompt...")
prompt, err = openai.request_body(pdf_text=text,
                                         invoice_type=model)
if err:
    raise Exception(f"Error: {err}")
print("Prompt loaded successfully.")

print("Making OpenAI request...")
gpt_output, err = openai.openai_request(prompt)
if err:
    raise Exception(f"Error: {err}")
print("OpenAI request completed successfully.")

json_out = json.loads(gpt_output)

print(json_out)

result = validate_values(json_out)
print(result)