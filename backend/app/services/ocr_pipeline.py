import logging
from pathlib import Path
from app.services.processors.base import ExtractedDocument, ExtractedPage

logger = logging.getLogger(__name__)

def perform_ocr(file_path: Path) -> ExtractedDocument:
    """
    Performs OCR text extraction on the PDF or image file.
    Renders pages to images and runs Tesseract if available, otherwise falls back gracefully.
    """
    pages = []
    
    try:
        import pytesseract
        from PIL import Image
        import fitz
        
        doc = fitz.open(str(file_path))
        for page_num, page in enumerate(doc, start=1):
            # Render page as image
            pix = page.get_pixmap(dpi=150)
            img_data = pix.tobytes("png")
            
            import io
            img = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(img).strip()
            
            if text:
                pages.append(ExtractedPage(
                    page_number=page_num,
                    raw_text=text,
                    markdown=text
                ))
        doc.close()
    except Exception as exc:
        logger.warning("pytesseract/PIL not fully available or failed during OCR. Using fallback: %s", exc)
        # Fallback to basic PyMuPDF text or simulated OCR text
        try:
            import fitz
            doc = fitz.open(str(file_path))
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                if not text:
                    text = f"[OCR Fallback: Image content on Page {page_num}]"
                pages.append(ExtractedPage(
                    page_number=page_num,
                    raw_text=text,
                    markdown=text
                ))
            doc.close()
        except Exception:
            pages.append(ExtractedPage(
                page_number=1,
                raw_text="[OCR Fallback: File content could not be read]",
                markdown="[OCR Fallback: File content could not be read]"
            ))

    return ExtractedDocument(pages=pages)
