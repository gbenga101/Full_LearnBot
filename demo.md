# LearnBot — Quick Demo Guide

This file explains how to run and demo LearnBot locally, and outlines the small UI dev controls (model selector, Info button, welcome modal behavior) we added.

## Quick start (local)

1. Ensure `.env` (or environment) contains a valid Gemini API key:

```bash
# Linux / macOS
export GEMINI_API_KEY="your_gemini_key_here"
python app.py

# Windows PowerShell
$env:GEMINI_API_KEY = "your_gemini_key_here"
python app.py
```

2. Serve the frontend (open `index.html` with Live Server or any static server):

```bash
# using npm http-server (optional)
npx http-server frontend -p 5500
# then open http://127.0.0.1:5500
```

3. Open the page in a browser. By default, the welcome modal shows on each page load. Use the header select to switch provider (LearnBot/Gemini or Local T5). The selection persists for the browser tab session.

## Controls & Developer toggles

- **Model selector (header):** Choose `LearnBot (Gemini)` or `Local T5 (flan-t5)`.
- **Info button (header):** Re-open the welcome modal any time. This forces the modal to reappear even if previously closed.
- **Welcome modal checkbox:** "Show once per tab" — when checked, the modal will show only once per tab session (previous behavior). When unchecked, modal shows every load.
- **Dev shortcut:** `Shift+W` toggles the welcome modal behavior between `always` and `session` and posts a small confirmation message in the chat.

## Expected demo flow

1. Start backend (`python app.py`) and ensure console shows `LearnBot API is running`.
2. Open frontend and type a short text like "Explain photosynthesis".
3. Choose explanation level via the gear (Layman / 12-Year-Old).
4. Pick the model in the header (Gemini vs T5) and click **Send**.
5. Watch the server logs (Flask) and browser console for the outgoing request and provider used.

## Troubleshooting steps (quick)

1. **If both providers return identical results** — run the backend debug curl tests (see below). If backend returns correct provider-specific output, the issue is frontend not sending the correct `provider` value.

2. **Curl tests** (run from terminal):

```bash
# Gemini
curl -X POST http://127.0.0.1:5000/simplify \
 -H "Content-Type: application/json" \
 -d '{"text":"Explain photosynthesis","level":"layman","provider":"gemini"}'

# T5
curl -X POST http://127.0.0.1:5000/simplify \
 -H "Content-Type: application/json" \
 -d '{"text":"Explain photosynthesis","level":"layman","provider":"t5"}'
```

3. **If Gemini returns unauthorized (403)** — check `GEMINI_API_KEY` and that `services/gemini_api.py` attaches the key correctly (`?key=...` or an `Authorization` header depending on your config).

4. **View browser request** — open DevTools > Network > check the outgoing `/simplify` request payload; confirm `provider` field is present and correct.

## Sidebar history behavior (how it works)

- The chat history is stored in `sessionStorage` as `learnbot_chat_history` (last 40 messages). It is restored on page reload.
- The left sidebar is populated with recent user messages (clicking an item will populate the input with that text so you can send it again or edit it before sending).

## Notes for the presenter

- Keep your terminal visible during the demo to show server logs and the provider used. If a provider fails due to API key or rate-limits, switch to the other provider in the header.
- For demonstration clarity: use short inputs and show both providers side-by-side with same prompt to compare output quality.

## Contact / Next steps

If something behaves unexpectedly during your demo, copy the server log output and the browser console network payload and paste it back to the developer for quick diagnosis.

