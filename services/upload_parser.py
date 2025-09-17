# services/upload_parser.py
import os
import tempfile
import logging
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import pdfplumber

logger = logging.getLogger(__name__)

IMAGE_EXTS = {"png", "jpg", "jpeg", "bmp", "gif", "tiff", "tif"}
PDF_EXTS = {"pdf"}

MAX_FILE_SIZE = 25 * 1024 * 1024

def image_preprocess_for_ocr(image_path):
    try:
        img = Image.open(image_path)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        return img
    except Exception as e:
        logger.exception("image_preprocess_for_ocr error: %s", e)
        raise

def ocr_image_file(path):
    try:
        img = image_preprocess_for_ocr(path)
        text = pytesseract.image_to_string(img, lang='eng')
        return text or ""
    except Exception as e:
        logger.exception("ocr_image_file error: %s", e)
        return ""

def extract_text_from_pdf(path):
    # First try text-layer extraction via pdfplumber
    text_chunks = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)
    except Exception as e:
        logger.warning("pdfplumber failed: %s", e)

    combined = "\n\n".join([p for p in text_chunks if p and p.strip()])
    if combined.strip():
        return combined

    # Fallback to image->OCR using pdf2image if available
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(path, dpi=200)
        ocr_texts = []
        for p_img in pages:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
                p_img.save(tmp_img.name, format="PNG")
                ocr_texts.append(ocr_image_file(tmp_img.name))
                try:
                    os.remove(tmp_img.name)
                except Exception:
                    pass
        return "\n\n".join(t for t in ocr_texts if t and t.strip())
    except Exception as e:
        logger.exception("PDF->image fallback failed (pdf2image missing or failed): %s", e)
        return ""

def extract_text_from_docx(path):
    try:
        from docx import Document
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        logger.exception("DOCX parsing failed: %s", e)
        return ""

def read_text_file(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as fh:
            return fh.read()
    except Exception as e:
        logger.exception("read_text_file failed: %s", e)
        return ""

def parse_uploaded_file(temp_path: str, ext: str) -> dict:
    """
    Returns a dict with keys:
      - extracted_text (str)
      - pages (int, optional)
      - warnings (list)
    """
    ext = ext.lower()
    result = {"extracted_text": "", "pages": 0, "warnings": []}

    if ext in IMAGE_EXTS:
        result["extracted_text"] = ocr_image_file(temp_path)
        result["pages"] = 1
        return result

    if ext in PDF_EXTS:
        txt = extract_text_from_pdf(temp_path)
        result["extracted_text"] = txt
        # crude page count attempt
        try:
            import pdfplumber
            with pdfplumber.open(temp_path) as pdf:
                result["pages"] = len(pdf.pages)
        except Exception:
            result["pages"] = 0
        return result

    if ext == "docx":
        result["extracted_text"] = extract_text_from_docx(temp_path)
        return result

    if ext == "txt":
        result["extracted_text"] = read_text_file(temp_path)
        return result

    result["warnings"].append("Unsupported extension in parser")
    return result
