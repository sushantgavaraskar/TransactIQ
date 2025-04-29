import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path

# Set the Tesseract path (Update this based on your system installation)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(pdf_path: str) -> str:
    """Extracts text from a PDF, handling both text-based and image-based PDFs."""
    pdf_path = Path(pdf_path)

    # Check if the PDF contains selectable text
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # Extract text from each page

    if text.strip():  # If text is found, return it
        return text.strip()

    # If no text is found, treat it as an image-based PDF
    images = convert_from_path(str(pdf_path), poppler_path=r"C:\poppler-24.08.0\Library\bin")  # Convert PDF pages to images
    extracted_text = ""

    for img in images:
        extracted_text += pytesseract.image_to_string(img) + "\n"  # Perform OCR

    return extracted_text.strip() if extracted_text else "No text could be extracted."
