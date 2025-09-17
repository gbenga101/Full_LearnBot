# routes/upload.py
import os
import io
import tempfile
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

# OCR / parsing libs
from PIL import Image, ImageOps, ImageFilter
import pytesseract

# Optional: pdfplumber for better PDF text extraction (multi-page)
import pdfplumber

# Optional: python-docx for .docx parsing
from docx import Document

upload_bp = Blueprint("upload", __name__)
logger = logging.getLogger(__name__)

# Allowed extensions & MIME hints we will accept for DOCX/TXT + images + pdf
ALLOWED_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif", "bmp", "tiff", "tif", "pdf", "docx", "txt"
}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB cap for safety

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def file_size_ok(file_obj):
    # werkzeug FileStorage has .content_length sometimes; fallback to in-memory check
    try:
        if hasattr(file_obj, 'content_length') and file_obj.content_length:
            return file_obj.content_length <= MAX_FILE_SIZE
    except Exception:
        pass
    # fallback read check (non-destructive)
    try:
        file_obj.stream.seek(0, os.SEEK_END)
        size = file_obj.stream.tell()
        file_obj.stream.seek(0)
        return size <= MAX_FILE_SIZE
    except Exception:
        # if we can't determine, allow and rely on temp file checks
        return True

def image_preprocess_for_ocr(image_path):
    """
    Basic preprocessing pipeline to improve OCR accuracy:
    - convert to grayscale
    - auto-contrast
    - optionally apply a slight median filter to reduce noise
    - return a PIL Image instance
    """
    img = Image.open(image_path)
    # convert to RGB if palette or others
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    # convert to grayscale
    img = ImageOps.grayscale(img)
    # increase contrast
    img = ImageOps.autocontrast(img)
    # slight denoise
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img

def ocr_image_file(path):
    """
    Run Tesseract OCR on an image file and return extracted text.
    """
    try:
        img = image_preprocess_for_ocr(path)
        text = pytesseract.image_to_string(img, lang='eng')
        return text or ""
    except Exception as e:
        logger.exception("OCR image extraction failed: %s", e)
        return ""

def extract_text_from_pdf(path):
    """
    Try to extract textual content from a PDF.
    Strategy:
      1) Use pdfplumber to extract text from each page (fast when PDF contains selectable text).
      2) If extracted text is empty across pages, fallback to rendering pages as images and run OCR.
    """
    text_chunks = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)
    except Exception as e:
        logger.warning("pdfplumber failed to read PDF as text: %s", e)
        # we'll fallback to OCR path below

    combined = "\n\n".join([p for p in text_chunks if p and p.strip()])
    if combined.strip():
        return combined

    # Fallback: rasterize each page and OCR (basic fallback, best-effort)
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(path, dpi=200)
        ocr_texts = []
        for p_img in pages:
            # save PIL image to temp file-like and OCR via pytesseract
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
                p_img.save(tmp_img.name, format="PNG")
                ocr_texts.append(ocr_image_file(tmp_img.name))
                try:
                    os.remove(tmp_img.name)
                except Exception:
                    pass
        return "\n\n".join(t for t in ocr_texts if t and t.strip())
    except Exception as e:
        logger.exception("PDF->image fallback OCR failed (pdf2image missing or failed): %s", e)
        return ""


def extract_text_from_docx(path):
    """
    Extract plain text from a DOCX file using python-docx.
    """
    try:
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        logger.exception("DOCX parsing failed: %s", e)
        return ""


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    # Basic checks
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    if not file_size_ok(file):
        return jsonify({"error": f"File too large. Max size is {MAX_FILE_SIZE} bytes."}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()

    # Save to temp file
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=f".{ext}")
    os.close(tmp_fd)
    try:
        file.save(tmp_path)
    except Exception as e:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        logger.exception("Failed to save uploaded file: %s", e)
        return jsonify({"error": "Failed to save uploaded file"}), 500

    extracted_text = ""
    try:
        if ext in ("png", "jpg", "jpeg", "bmp", "gif", "tiff", "tif"):
            # image path -> OCR
            extracted_text = ocr_image_file(tmp_path)

        elif ext == "pdf":
            extracted_text = extract_text_from_pdf(tmp_path)

        elif ext == "docx":
            extracted_text = extract_text_from_docx(tmp_path)

        elif ext == "txt":
            # plain text
            try:
                with open(tmp_path, "r", encoding="utf-8") as fh:
                    extracted_text = fh.read()
            except UnicodeDecodeError:
                with open(tmp_path, "r", encoding="latin-1") as fh:
                    extracted_text = fh.read()
        else:
            extracted_text = ""

    finally:
        # always cleanup temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    if not extracted_text or not extracted_text.strip():
        return jsonify({"error": "No text could be extracted from the file"}), 422

    # Return normalized key that the frontend expects
    return jsonify({"extracted_text": extracted_text}), 200