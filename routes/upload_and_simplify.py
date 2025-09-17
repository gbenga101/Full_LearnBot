# routes/upload_and_simplify.py
import os, tempfile, logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from services.upload_parser import parse_uploaded_file
from services.text_simplifier import simplify_text  # ensure this function exists as pipeline entry

upload_and_simplify_bp = Blueprint("upload_and_simplify", __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTS = {"png","jpg","jpeg","bmp","gif","tiff","tif","pdf","docx","txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTS

@upload_and_simplify_bp.route("/upload-and-simplify", methods=["POST"])
def upload_and_simplify():
    if "file" not in request.files:
        return jsonify({"error":"No file part"}), 400
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error":"No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error":"Unsupported file type"}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".",1)[1].lower()

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=f".{ext}")
    os.close(tmp_fd)
    try:
        file.save(tmp_path)
    except Exception as e:
        try: os.remove(tmp_path)
        except: pass
        logger.exception("Failed to save uploaded file: %s", e)
        return jsonify({"error":"Failed to save uploaded file"}), 500

    try:
        parsed = parse_uploaded_file(tmp_path, ext)
        text = parsed.get("extracted_text","").strip()
        if not text:
            return jsonify({"error":"No text extracted", "pages": parsed.get("pages",0)}), 422

        # provider preference from form (or default to 'gemini')
        provider = request.form.get("provider") or request.args.get("provider") or "gemini"

        # simplify_text should be your pipeline entry that handles provider/fallback
        simplified = simplify_text(text, provider=provider)

    except Exception as e:
        logger.exception("upload_and_simplify error: %s", e)
        return jsonify({"error": str(e)}), 500
    finally:
        try: os.remove(tmp_path)
        except Exception: pass

    return jsonify({
        "filename": filename,
        "extracted_text": text,
        "simplified_text": simplified,
        "provider": provider,
        "pages": parsed.get("pages", 0),
        "warnings": parsed.get("warnings", [])
    }), 200
# --- End of upload_and_simplify.py ---