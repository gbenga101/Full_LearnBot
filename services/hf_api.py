import os, requests, logging

logger = logging.getLogger(__name__)

class HFSimplifier:
    def __init__(self):
        self.api_key = os.getenv("HF_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        self.api_url = "https://api-inference.huggingface.co/models"
        # Try these in order until one works
        self.models = [
            "facebook/bart-large-cnn",
            "google/flan-t5-base",
            "google/flan-t5-small",
        ]

    def simplify(self, text: str, level: str) -> str:
        if not self.api_key:
            return "⚠️ Hugging Face API key not configured."

        prompt = (
            f"LearnBot is an AI teacher with 20+ years of experience. "
            f"Explain the following text for a {level} learner in the clearest way possible. "
            f"Be concise, use simple words, and give a short example if helpful.\n\n"
            f"Text to simplify: {text}"
        )

        for model in self.models:
            try:
                logger.debug("📡 Trying HF model: %s", model)
                resp = requests.post(
                    f"{self.api_url}/{model}",
                    headers=self.headers,
                    json={"inputs": prompt},
                    timeout=30
                )
                if resp.status_code != 200:
                    logger.debug("HF model %s returned %s", model, resp.status_code)
                    continue

                data = resp.json()
                logger.debug("HF raw response: %s", data)

                # Normalize response
                simplified = None
                if isinstance(data, list):
                    texts = []
                    for item in data:
                        if isinstance(item, dict):
                            if "summary_text" in item:
                                texts.append(item["summary_text"])
                            elif "generated_text" in item:
                                texts.append(item["generated_text"])
                    simplified = " ".join(texts).strip() if texts else None
                elif isinstance(data, dict):
                    simplified = data.get("summary_text") or data.get("generated_text")

                if simplified:
                    logger.info("✅ Hugging Face model %s succeeded", model)
                    return simplified

            except Exception as e:
                logger.warning("HF model %s failed: %s", model, e)

        return "⚠️ All Hugging Face models failed."
