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


from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class T5Simplifier:
    def __init__(self, model_name="google/flan-t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def simplify(self, text, level="layman"):
        # Improved prompt for better simplification
        """ prompt = (
            f"Please simplify the following text for a {level} learner:\n\n"
            f"{text}\n\n"
            "Simplified version:"
        ) """
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
        return result.strip()