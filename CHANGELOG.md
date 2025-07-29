# **Changelog: AI-Driven Personalized Learning System**

## **Introduction**
This changelog documents the development process of the AI-Driven Personalized Learning System, integrating a pre-existing frontend (`LearnBot`) hosted on GitHub Pages (`https://gbenga101.github.io/LearnBot`) with a new Flask-based backend. The project aims to simplify academic content using the Google Gemini API, with OCR for file processing and session-based memory. Development started on July 27, 2025, with an entry-level frontend developer and expert AI guidance.

**Environment**:
- **OS**: Windows 10
- **IDE**: VS Code
- **Hardware**: Toshiba Portege R930 (4GB RAM, 250GB SSD, 2.7GHz 3rd Gen Intel)
- **Frontend**: Pure HTML, CSS (Bootstrap), JavaScript
- **Backend**: Python 3.13 with Flask

## **Milestones**

### **Milestone 0: Project Initialization and Planning (July 27-28, 2025)**

**Goals**:
- Define project scope and structure.
- Integrate existing frontend with backend planning.

**Tasks Completed**:
- **Project Discussion and Requirements**:
  - Identified project goals: text simplification, file processing (PDFs/images), session memory.
  - Assessed hardware constraints and set a 2-week roadmap.
- **Backend Structure Proposed**:
  - Designed a modular structure:
    - `app.py`: Main Flask app.
    - `config/`: Configuration (e.g., API keys).
    - `routes/`: API endpoints.
    - `services/`: Business logic (e.g., Gemini API, OCR).
    - `static/`: Upload storage.
    - `tests/`: Testing scripts.
  - Planned integration with frontend.
- **Frontend Integration Planning**:
  - Reviewed existing `LearnBot` frontend structure (assets, css, js, index.html, etc.).
  - Decided to move `LearnBot` into `frontend/` subdirectory for local development.

**Tools**:
- VS Code, Git

**Challenges**:
- Ensuring frontend move doesn’t affect GitHub Pages accessibility.
- Hardware limitations (4GB RAM) noted for future optimization.

**Success Criteria**:
- Structure defined and frontend move planned.

---

### **Milestone 1: Environment Setup and Frontend Move (July 27-28, 2025)**

**Goals**:
- Set up development environment.
- Move and verify frontend structure.

**Tasks Completed**:
- **Verify Python Installation**:
  - Confirmed Python 3.13 and pip installed (via `pip show` paths: `C:\Users\fagbe\AppData\Local\Programs\Python\Python313\`).
- **Create Project Directory and Initialize Git**:
  - Created `personalized-learning-system` folder (later renamed to `Full_LearnBot`).
  - Initialized Git with `.gitignore`:
    ```
    __pycache__/
    *.pyc
    venv/
    *.env
    static/uploads/
    api_key.txt
    ```
  - Committed initial setup.
- **Plan Backend Structure**:
  - Defined file paths (config, routes, services, etc.) as outlined.
- **Move Frontend into `frontend/`**:
  - Backed up `LearnBot` folder.
  - Moved `LearnBot` contents (assets, css, js, index.html, etc.) into `frontend/`.
  - Verified all files intact and `index.html` loads locally without errors.
- **Update `.gitignore`**:
  - Added `frontend/node_modules/` (future-proofing).
  - Committed changes.
- **Test Local Frontend**:
  - Opened `frontend/index.html` in browser, confirmed functionality with Bootstrap CSS.
- **Install Flask and Dependencies**:
  - Installed Flask and Requests using `pip install -r requirements.txt`.
  - Verified installations:
    - Flask: 3.0.3
    - Requests: 2.32.3
  - Committed changes to Git.

**Tools**:
- VS Code, Git, File Explorer

**Challenges**:
- Ensured no impact on live GitHub Pages site (`https://gbenga101.github.io/LearnBot`).
- Handled manually due to no npm.

**Success Criteria**:
- Frontend moved and testable locally.
- Backend structure ready for setup.
- Dependencies installed.

**Notes**:
- Live site remains unaffected; local changes only.
- Stopped at 01:50 AM WAT, July 28, 2025, after installing dependencies.

---

### **Milestone 2: Backend Setup and Gemini API Integration (July 28-29, 2025)**

**Goals**:
- Set up backend files and configuration.
- Integrate and test Google Gemini API for text simplification.

**Tasks Completed**:
- **Rename Project Directory**:
  - Renamed `personalized-learning-system` to `Full_LearnBot` to align with developer preference.
  - Updated all references to use `Full_LearnBot` as the root directory.
- **Create Backend Files**:
  - Created `config/config.py` with `.env` support for `GEMINI_API_KEY` and `UPLOAD_FOLDER`.
  - Installed `python-dotenv` (`pip install python-dotenv`) for secure key management.
  - Updated `.gitignore` to include `/.env`.
  - Created `services/gemini_api.py` with `TextSimplifier` class for Gemini API calls.
- **Obtain Google Gemini API Key**:
  - Generated API key via Google AI Studio and stored it in `.env`.
- **Test Flask App**:
  - Ran `app.py` and verified “Hello, World! Backend is running” at `http://127.0.0.1:5000/`.
- **Implement and Test Gemini API**:
  - Developed `simplify_text` method in `gemini_api.py` to simplify text for “Layman” level.
  - Debugged import issues (`ModuleNotFoundError: No module named 'config'`) by ensuring correct directory (`Full_LearnBot`).
  - Added logging for debugging API responses.
  - Successfully simplified text (e.g., “Advanced mathematics involves calculus...” → “High-level math uses calculus (finding areas of shapes)...”).
  - Tested with document text: “Studies, such as that by A. Abub-Sake... ” → “A recent study shows that AI tools tailored to specific places...”.
- **Commit Changes**:
  - Regularly committed updates to Git, ensuring a clean working tree.

**Tools**:
- VS Code, Git, Python Shell, Google AI Studio

**Challenges**:
- Resolved path issues due to directory context (running from `Full_LearnBot`).
- Adjusted prompt engineering to force direct simplification from Gemini API.
- Managed hardware constraints during long debugging sessions.

**Success Criteria**:
- Backend files created and functional.
- Gemini API integrated and simplifying text successfully.
- Logging and debugging implemented.

**Notes**:
- Stopped at 03:42 AM WAT, July 29, 2025, after successful API testing.
- Prompt engineering for better layman explanations planned for tomorrow (8:00 PM WAT).

---

## **Pending Tasks (To Resume)**

- **Milestone 2 Continuation**:
  - Refine prompt engineering for more engaging layman explanations.
  - Integrate `/simplify` route in `routes/api.py`.
- **Milestone 3**:
  - Connect frontend to backend via API calls.
  - Implement OCR with Tesseract.
  - Add session memory using `sessionStorage`.

## **Environment Setup**
- **Python**: 3.13.5 (confirmed installed).
- **Flask**: 3.0.3 (installed).
- **Requests**: 2.32.3 (installed).
- **python-dotenv**: Installed for `.env` support.
- **Tesseract**: Planned for Week 2 OCR.

## **Future Enhancements**
- OCR integration for PDF/image processing.
- Session memory with `sessionStorage` for user context.
- Local testing and deployment adjustments.
- Optimize for 4GB RAM constraints.

## **Conclusion**
Progress is on track with frontend integration, backend setup, and Gemini API integration complete. The `TextSimplifier` successfully simplifies academic text for layman audiences, with debugging and logging in place. The next session will focus on prompt engineering and backend-frontend connectivity. Save this file in the project root (`Full_LearnBot/CHANGELOG.md`) for reference.