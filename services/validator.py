# services/validator.py
import re
import logging
from typing import Optional, Dict
from services.exceptions import APIError

logger = logging.getLogger(__name__)

SECTION_HEADINGS = ["Simple Explanation", "Key Points"]

def _normalize_bullets(text: str) -> str:
    # Normalize common bullet markers to "- "
    text = re.sub(r"^[\s]*•[\s]*", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s]*\*\s+", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s]*–\s+", "- ", text, flags=re.MULTILINE)
    # Ensure single blank line between sections
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _extract_sections(raw: str) -> Dict[str, str]:
    """
    Attempt to reliably extract the two required sections:
      1) Simple Explanation
      2) Key Points
    Returns dict with keys 'simple' and 'key_points' (string).
    Raises APIError if extraction fails.
    """
    if not raw or not raw.strip():
        raise APIError("Empty provider output")

    txt = raw.strip()

    # Allow providers to return headings with or without punctuation
    # Try to locate "Simple Explanation" heading
    # Use case-insensitive search
    se_pattern = re.compile(r"(?:^|\n)\s*(Simple Explanation)\s*[:\-–]?\s*\n", re.IGNORECASE)
    kp_pattern = re.compile(r"(?:^|\n)\s*(Key Points)\s*[:\-–]?\s*\n", re.IGNORECASE)

    se_match = se_pattern.search(txt)
    kp_match = kp_pattern.search(txt)

    if se_match and kp_match:
        se_start = se_match.end()
        kp_start = kp_match.start()
        simple = txt[se_start:kp_start].strip()
        kp_section = txt[kp_match.end():].strip()
        # ensure key points are a list
        kp_section = _normalize_bullets(kp_section)
        return {"simple": simple, "key_points": kp_section}
    else:
        # Fallback heuristic: split on double-newline boundary and try to infer
        parts = re.split(r"\n\s*\n", txt)
        if len(parts) >= 2:
            # assume first block is explanation, last block contains bullets
            simple = parts[0].strip()
            key_points = "\n\n".join(parts[1:]).strip()
            key_points = _normalize_bullets(key_points)
            return {"simple": simple, "key_points": key_points}
        # give up with explanatory error
        logger.debug("Validator could not detect required headings. Raw output: %s", txt[:400])
        raise APIError("Provider output did not match required format (Simple Explanation + Key Points)")

def validate_and_format(raw: str) -> str:
    """
    Validate provider output, enforce format, return a cleaned, human-friendly string:
      Simple Explanation:\n<one paragraph>\n\nKey Points:\n- item1\n- item2
    Raises APIError on failure (so route fallback can handle it).
    """
    sections = _extract_sections(raw)
    simple = sections["simple"]
    key_points = sections["key_points"]

    # Ensure simple is a single short paragraph (truncate if too long)
    simple = " ".join(simple.splitlines()).strip()
    if len(simple.split()) > 200:
        # don't silently lose meaning; trim to 200 words with ellipsis
        simple_words = simple.split()
        simple = " ".join(simple_words[:200]) + "..."

    # Ensure key_points lines start with "- "
    kp_lines = []
    for line in key_points.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.startswith("- "):
            # strip numbering like "1. " or "• " etc
            line = re.sub(r"^\d+\.\s*", "", line)
            if not line.startswith("- "):
                line = "- " + line
        kp_lines.append(line)

    if not kp_lines:
        raise APIError("Key Points section empty after parsing")

    formatted = f"Simple Explanation:\n{simple}\n\nKey Points:\n" + "\n".join(kp_lines)
    return formatted
