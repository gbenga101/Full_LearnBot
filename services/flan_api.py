from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
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
        return result