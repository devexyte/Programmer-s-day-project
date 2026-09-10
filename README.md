# Ruia AI Student Companion

A premium Streamlit academic companion for Ruia College students. It combines a personalised study planner, deadline reminders, resume feedback, quiz generation and exam revision planning with Gemini and MySQL persistence.

## Run locally

1. Create a MySQL database by running `schema.sql` in MySQL.
2. Copy `.env.example` to `.env`, then add the MySQL connection details and a Gemini API key.
3. Install dependencies: `pip install -r requirements.txt`
4. Start the application: `streamlit run app.py`

## Architecture

- `frontend/` contains independently rendered Streamlit views.
- `backend/db.py` provides parameterised MySQL access and transaction handling.
- `backend/*_logic.py` contains feature-specific prompt workflows.
- `backend/ai.py` is the single Gemini integration boundary.
- `assets/styles.css` implements the Ruia-inspired maroon, gold and serif editorial design.

## Deployment

Deploy to Streamlit Community Cloud, Render or Railway. Configure all variables from `.env.example` as platform secrets and use a managed MySQL service. Apply `schema.sql` once before the first launch. Never commit `.env` or API keys.

## Optional enhancements

Add college SSO, timetable import, calendar sync, role-based faculty dashboards, and an approved Ruia crest asset once brand permission is available.
