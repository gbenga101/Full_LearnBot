# services/flan_api.py

import os
import requests

class T5Simplifier:
    def __init__(self, model_name="google/flan-t5-base"):
        self.model_name = model_name
        self.api_token = os.getenv("HF_API_TOKEN")
        if not self.api_token:
            raise ValueError("⚠️ Missing Hugging Face API token. Please set HF_API_TOKEN in your .env")

    def simplify(self, text, level="layman"):
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