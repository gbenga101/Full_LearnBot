# quick manual test (not unittest framework) - run with python tests/test_simplifier.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.text_simplifier import simplify_text

samples = [
    ("What is a noun? Explain for an SS2 student.", "auto"),
    ("Explain photosynthesis simply.", "gemini"),
    ("Explain mitosis simply.", "openrouter"),
]

for text, provider in samples:
    try:
        print("====", provider, "====")
        out = simplify_text(text, provider=provider)
        print(out[:1000])  # print a chunk
    except Exception as e:
        print("ERROR:", e)