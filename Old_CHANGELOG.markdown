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
  - Created `personalized-learning-system` folder.
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

## **Pending Tasks (To Resume)**

- **Milestone 1 Continuation**:
  - Create backend files (app.py, config.py, etc.).
  - Obtain Google Gemini API key.
  - Test Flask app and Gemini API.
- **Milestone 2**:
  - Connect frontend to backend.
  - Implement `/simplify` route.

## **Environment Setup**
- **Python**: 3.13 (confirmed installed).
- **Flask**: 3.0.3 (installed).
- **Requests**: 2.32.3 (installed).
- **Tesseract**: Planned for Week 2 OCR.

## **Future Enhancements**
- OCR integration.
- Session memory with `sessionStorage`.
- Local testing and deployment adjustments.

## **Conclusion**
Progress is on track with frontend integration and environment setup complete locally. Next session will focus on backend file creation and API integration. Save this file in the project root (`personalized-learning-system/CHANGELOG.md`) for reference.

