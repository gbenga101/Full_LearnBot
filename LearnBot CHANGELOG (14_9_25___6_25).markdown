## [2025-09-15]
### Changed
- Converted provider adapters to raise typed exceptions for robust fallback control:
  - Added `services/exceptions.py` with `RateLimitError`, `APIError`, `NetworkError`.
  - `services/gemini_api.py` updated to raise exceptions on 429/HTTP/network/parse errors.
  - `services/openrouter_api.py` updated to raise exceptions on 429/HTTP/network/parse errors and maintain retry/backoff behavior.
- `routes/api.py` updated to catch typed provider exceptions and follow the fallback chain cleanly (Gemini → OpenRouter → OpenAI). OpenAI call kept backward-compatible handling of string error messages.
- Improved prompt in `services/gemini_api.py`:
  - Enhanced clarity and engagement for LearnBot’s persona, emphasizing summarization, conversational tone, and structured output.
  - Added guidelines for concise summarization, jargon explanation, relatable examples, and avoiding oversimplification.
- Improved prompts in `services/openrouter_api.py`:
  - Updated `SYSTEM_PROMPT_BASE` to emphasize summarization, engagement, and structured output (Simple Explanation + Key Points).
  - Updated `LEVEL_PROMPTS` to improve clarity and alignment with LearnBot’s educational goals.
  - Merged `layman` and `ss2` prompts into a single `layman` prompt, supporting both adult learners and senior secondary students with clear language, defined key terms, and relatable examples.
  - Removed `ss2` option, retaining only `layman` and `12yo` in `LEVEL_PROMPTS`.
  - Tweaked `12yo` prompt to require explicit technical term explanations in the Simple Explanation paragraph and ensure complete paragraphs.
### Fixed / Verified
- OpenRouter privacy setting resolved; OpenRouter returns valid simplified content (observed: 429 then success).
- Removed Hugging Face hosted usage from active fallback chain (previously removed).
- Addressed potential incomplete “Simple Explanation” in `openrouter_api.py` by updating `SYSTEM_PROMPT_BASE` to require a complete, standalone paragraph.
### Pending
- (Optional) Replace OpenAI adapter to raise same typed exceptions for full consistency (currently still treated as returning strings).
- Run a final suite of sample inputs for format consistency and UX checks (layman, 12yo).
- Monitor OpenRouter 429 rate-limiting errors and consider increasing `OPENROUTER_MAX_RETRIES` or `OPENROUTER_BACKOFF_BASE` if frequent.