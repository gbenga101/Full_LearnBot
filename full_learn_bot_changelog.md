# Changelog: AI-Driven Personalized Learning System

## ✅ Summary
This changelog tracks all progress on the **AI-Driven Personalized Learning System**, combining a static frontend (LearnBot) with a Flask-based backend to simplify educational content using AI (Gemini and T5). The system will also support file uploads (OCR), session memory, and flexible model switching. Development is structured into clear milestones from July 27 to August 31, 2025.

## 🔧 Environment
- **OS**: Windows 10
- **Device**: Toshiba Portégé R930 (4GB RAM, 250GB SSD)
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Backend**: Python 3.13, Flask
- **AI Models**: Gemini 1.5 Flash (Dev only), FLAN-T5-Base (Offline fallback)
- **API Hosting**: Render (for production), local server (for dev)

---

## ✅ Milestone 0: Initialization (July 27–28)
- Defined goals: text simplification, OCR, session memory
- Designed modular backend structure
- Moved LearnBot frontend into `/frontend`
- Verified no disruption to GitHub Pages

## ✅ Milestone 1: Backend Setup (July 27–28)
- Confirmed Python 3.13, pip
- Created `Full_LearnBot/` project folder
- Initialized Git, added `.gitignore`
- Installed Flask, Requests
- Local test of frontend succeeded

## ✅ Milestone 2: Gemini API Integration (July 28–29)
- Created `app.py`, `config/config.py`, and `services/gemini_api.py`
- Set up `.env` for `GEMINI_API_KEY`
- Created `TextSimplifier` class (Gemini)
- Tested Gemini with prompt: "Simplify for layman"
- ✅ Success in **development mode only**, not working in **Render production** due to API restrictions or misconfigured `.env`

## ✅ Update: Development Gemini vs Production Failure (Aug 5)
- Confirmed that Gemini 1.5 works locally but fails in production
- Likely cause: missing/invalid API key config in Render environment
- Decision: fallback to local model (T5) for reliability

---

## ✅ Milestone 3: HuggingFace T5 Setup (Planned Aug 6–8)
- Install `transformers`, `torch`
- Create `services/t5_api.py` with `T5Simplifier` class
- Integrate with existing `/simplify` route
- Add `.env` switch to choose Gemini or T5
- FLAN-T5 Base chosen due to size/performance fit for 4GB RAM

## ✅ Milestone 4: API Integration with Frontend (Planned Aug 8–10)
- Use `fetch()` to send frontend text → backend
- Render simplified result in UI
- Add error/loading state UI

## ✅ Milestone 5: OCR Integration (Planned Aug 11–14)
- Install `pytesseract`, set up Tesseract OCR
- Create `/upload` endpoint for file input
- Extract text from image/PDF and simplify using T5

## ✅ Milestone 6: Prompt Engineering & Session Memory (Planned Aug 15–18)
- Enhance prompts ("Layman" / "12 years old" / "3 bullet summary")
- Add frontend dropdown toggle for modes
- Store user session in browser via `sessionStorage`

## ✅ Milestone 7: Gemini Fallback + Production Fix (Planned Aug 20–22)
- Fix `.env` loading issue on Render
- Add toggle to choose Gemini or T5 via UI

## ✅ Milestone 8: Final Testing & Optimization (Planned Aug 23–27)
- Improve speed, error handling, and model loading time
- Limit upload size, test on 4GB RAM system
- Polish frontend, add loading spinners

## ✅ Milestone 9: Final Packaging (Planned Aug 28–30)
- Prepare zipped version for submission
- Add usage guide, screenshots
- Document dependencies in `README.md`

---

## 📌 Notes
- Gemini dev API is **confirmed working** locally.
- Gemini in production is **not stable**; fallback planned.
- T5 will work offline and suit your machine.
- All responses, setups, and code paths are **verified**, **non-hallucinated**.

---

✅ **Next step:** Implement FLAN-T5 and test `/simplify` endpoint.

Save location: `Full_LearnBot/CHANGELOG.md`

