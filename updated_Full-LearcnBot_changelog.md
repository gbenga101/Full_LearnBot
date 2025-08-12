# **Changelog: AI-Driven Personalized Learning System**

## **Introduction**
This changelog documents the development process of the AI-Driven Personalized Learning System, integrating the existing frontend (`LearnBot`) hosted on GitHub Pages (`https://gbenga101.github.io/LearnBot`) with a Flask-based backend. The project simplifies academic content using the Google Gemini API, supports file uploads (planned OCR), and uses session-scoped memory for UX. Development updates are recorded to ensure repeatable local demos and a stable deliverable for presentations.

**Environment**:
- **OS**: Windows 10
- **IDE**: VS Code
- **Hardware**: Toshiba Portégé R930 (4GB RAM, 250GB SSD, 3rd Gen Intel)
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Backend**: Python 3.x with Flask

---

## **Milestones**

### **Milestone 0: Project Initialization and Planning (July 27-28, 2025)**
(unchanged — initial planning, structure, and scope)

### **Milestone 1: Environment Setup and Frontend Move (July 27-28, 2025)**
(unchanged — frontend moved to `frontend/`, dependencies installed, Git init)

### **Milestone 2: Backend Setup and Gemini API Integration (July 28-29, 2025)**
(unchanged — `services/gemini_api.py` created, `config/.env` for GEMINI_API_KEY, prompt engineering, testing)

### **Milestone 3: Finalize MVP Backend & Connect to Frontend (Aug 1–2, 2025)**
**Completed**:
- Finalized `/simplify` route to accept JSON input (`text`, `level`) and return `{"simplified_text": "..."}`
- Frontend fetch integration completed: index.html + js/script.js send user input and display Gemini responses
- Prompt tuned for `layman` and `12-year-old` levels
- Verified end-to-end locally via `curl` and browser

---

## **Recent changes & fixes (Aug 8–11, 2025)**
**What was added / changed**:
- **Merged `/simplify` routing**: single route now accepts a `provider` field (`"gemini"` or `"t5"`) — defaults to Gemini. This allows future provider switching without frontend code edits.
- **Frontend model selector**: a model selector control was added to the header (HTML `<select id="modelSelect">`) so the user can switch provider per session.
- **Session-scoped provider persistence**: provider selection stored in `sessionStorage` as `learnbot_provider` (session-only by design).
- **Welcome modal**: a one-time per-tab modal (LearnBot intro) implemented and persisted via `sessionStorage` as `learnbot_welcomed`.
- **script.js update**: `sendMessage()` now includes `provider` in POST body; improved error handling, typing indicator, and UX consistency.
- **T5 route preserved**: `services/flan_api.py` (local T5 wrapper) remains available and callable via `provider: "t5"`, but **T5 work is currently paused** for this sprint.
- **Render / production paused**: due to Gemini production restrictions, focus is local development and demos only.
- **Config**: `config/config.py` continues to supply `GEMINI_API_KEY` and timeouts from `.env`. Ensure `GEMINI_API_KEY` is set for local runs.

**Why**:
- Keep the demo reliable locally (Gemini in dev works; production restricted).
- Provide fast provider switching for demos and future fallback plans.
- Add a friendly welcome for first-time users during a demo.

---

## **Pending / Next Tasks (priority for immediate demo)**
1. **Frontend stability**
   - Ensure header model selector is visible and working.
   - Add an "Info" button to re-open the welcome modal on demand (recommended).
2. **Error & logging polish**
   - Return friendly errors from server when API keys are missing or when provider fails.
   - Add server logs for failed third-party calls (no sensitive data in responses).
3. **Session memory**
   - Implement sessionStorage-based conversation memory so a user's last explanations persist across page reloads in the same tab.
4. **OCR (planned)**
   - Add the upload endpoint and Tesseract / pytesseract integration (Phase 3) — schedule after demo.
5. **OpenAI fallback (deferred)**
   - Keep OpenAI as a future fallback; do not add or enable until after the delivery month.
6. **Demo checklist**
   - Validate `GEMINI_API_KEY` in `.env`.
   - Confirm `window.API_BASE_URL` points to `http://127.0.0.1:5000/simplify` for local demo.
   - Run `curl` tests for Gemini and T5 to ensure route behavior.
   - Add small README `DEMO.md` describing how to run locally and the header selector usage.

---

## **Environment Setup (current)**
- Python 3.13.x
- Flask 3.x
- requests 2.32.x
- python-dotenv for `.env` support
- (Tesseract planned) — not yet installed

---

## **Decisions & Notes**
- **T5 work is paused** until after delivery this month — we will not change T5 code or run heavy local models during the demo sprint.
- **Production deployment paused** due to Gemini production key restrictions. Local dev will be used for presentations.
- **No OpenAI integration** for now — planned as an optional backup after the main delivery.

---

## **Changelog entry example for git commit**
`Added header model selector + session-based provider selection; merged /simplify route to accept provider; implemented welcome modal (session-based). T5 and OpenAI integrations paused for demo sprint.`

---

## **Save location**
Save this file at `Full_LearnBot/CHANGELOG.md`.

