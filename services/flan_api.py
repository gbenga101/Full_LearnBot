# services/flan_api.py
import os
import logging
import requests

logger = logging.getLogger(__name__)

class T5Simplifier:
    """Safe wrapper for a T5 simplifier. This variant will try HF model (same as HFSimplifier)
    but will never raise — it returns ⚠️-prefixed error strings on failure so fallback logic works."""
    def __init__(self, model_name="google/flan-t5-small"):
        self.model_name = model_name
        self.api_key = os.getenv("HF_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def simplify(self, text: str, level: str = "layman") -> str:
        if not self.api_key:
            return "⚠️ Hugging Face API key not configured for local T5 wrapper."

        prompt = (
            f"You are LearnBot, an AI teacher. Explain for a {level} learner:\n\n{text}"
        )
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 150, "temperature": 0.7}}
        url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=60)
            if resp.status_code != 200:
                logger.error("Local T5 wrapper HF call returned %s: %s", resp.status_code, resp.text)
                return f"⚠️ Hugging Face API error: {resp.status_code} - {resp.text}"
            data = resp.json()
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"].strip()
            return str(data)
        except Exception as e:
            logger.exception("Local T5 (HF) call failed")
            return f"⚠️ Local T5 error: {str(e)}"

        """
        Simplifies text using Hugging Face Inference API.
        """
        prompt = (
            f"You are a LearnBot, an AI teacher with 20+ years of experience. "
            f"Explain the following text for a {level} learner in the clearest way possible. "
            "Follow these rules:\n"
            "1. Use plain, everyday English.\n"
            "2. Keep it concise but do not skip important details.\n"
            "3. Use short sentences and simple words.\n"
            "4. When possible, give a quick example or analogy to make it relatable.\n"
            "5. Break information into bullet points or steps if it improves clarity.\n"
            "6. Avoid jargon unless you explain it.\n\n"
            f"Text to simplify:\n{text}"
        )

        url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 150, "temperature": 0.7}}

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error: {response.status_code} - {response.text}")

        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].strip()
        return str(result).strip()



""" from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class T5Simplifier:
    def __init__(self, model_name="google/flan-t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def simplify(self, text, level="layman"):
        prompt = f"Simplify this for a {level} level: {text}"
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(**inputs, max_new_tokens=150)
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result """

""" from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class T5Simplifier:
    def __init__(self):
        model_name = "google/flan-t5-base"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def simplify(self, text, level):
        # Generate prompt based on simplification level
        prompt = f"Simplify this text for a {level} level: {text}"

        # Tokenize and generate output
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_length=512,
            num_beams=4,
            early_stopping=True
        )

        # Decode and return the output
        simplified_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return simplified_text """


""" 
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class T5Simplifier:
    def __init__(self, model_name="google/flan-t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def simplify(self, text, level="layman"):
        # Improved prompt for better simplification
        prompt = (
            f"Simplify this text in very easy terms for a {level}-level learner. "
            f"Only give the simplified version. Text:\n\n{text}"
        )

        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            num_beams=4,
            early_stopping=True
        )

        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result.strip() """