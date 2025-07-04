# backend/extract.py
import os
import pytesseract
from pdf2image import convert_from_path
import pdfplumber


def extract_text_from_pdf(pdf_path):
    """
    Tries to extract text directly from PDF using pdfplumber.
    Falls back to OCR (image-to-text) only if text is missing on a page.
    Returns full extracted text.
    """
    full_text = ""
    
    print(f"🔍 Reading PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()

            if text and text.strip():
                # Text was found normally
                print(f"✅ Extracted text from page {i+1} using pdfplumber")
                full_text += f"\n--- Page {i+1} (pdfplumber) ---\n{text}"
            else:
                # Fallback: convert that page to image and use OCR
                print(f"🌀 Page {i+1} has no text — using OCR fallback")
                images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1, dpi=300)
                ocr_text = pytesseract.image_to_string(images[0])
                full_text += f"\n--- Page {i+1} (OCR) ---\n{ocr_text}"

    return full_text


if __name__ == "__main__":
    sample_path = "data/sample.pdf"
    if not os.path.exists(sample_path):
        print("❌ No sample PDF found at:", sample_path)
    else:
        result = extract_text_from_pdf(sample_path)
        print("\n--- First 2000 characters of Extracted Text ---\n")
        print(result[:2000])
