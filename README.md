# LLM Roadmap

A practical roadmap for learning to **use** large language models — from fundamentals and prompting through APIs, RAG, agents, evaluation, and shipping — with curated links to high-quality resources.

- `frontend/` — React (Vite) + React Router
- `backend/` — FastAPI serving roadmap/resource data

## Prerequisites

- Python 3.12+
- Node.js 20+ and npm

## Backend (FastAPI)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m app   # host/port come from .env (APP_HOST / APP_PORT)
```

- Health check: http://127.0.0.1:8001/api/health
- API docs: http://127.0.0.1:8001/docs
- Tests: `pytest`

Config (`backend/.env`): `APP_HOST`, `APP_PORT`, `CORS_ORIGINS` (comma-separated), `DATA_FILE`.
Default port is 8001 (8000 is often taken on Windows). If you change it, update `VITE_API_BASE_URL` in `frontend/.env` too.

### API

| Endpoint | Description |
| --- | --- |
| `GET /api/health` | Health check |
| `GET /api/stages` | Stage summaries in order (no resources; includes `resource_count`) |
| `GET /api/stages/{id}` | Full stage with goals and resources; `404` if unknown |
| `GET /api/resources?level=&type=&cost=&q=` | All resources (with `stage_id`/`stage_title`), filtered. `level`: beginner/intermediate/advanced; `type`: docs/course/video/article/tool/repo; `cost`: free/paid; `q`: case-insensitive search over title, description, provider (max 100 chars). Invalid values return `422`. |

### Roadmap data

All content lives in `backend/app/data/roadmap.v1.json` (versioned via `version`/`updated` fields). It is validated against the Pydantic models in `app/models.py` on load; stage and resource ids must be unique. Edit the JSON and restart the server to update content.

## Frontend (React + Vite)

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open http://localhost:5173. Config (`frontend/.env`): `VITE_DEV_PORT`, `VITE_BASE_PATH` (production base path, default `/ai-made-easy/`).

The site is fully static: content is bundled from `frontend/src/data/roadmap.json` through `src/content.js` (the one place to swap in an API later). The backend is not needed to run or build it.

- `npm test` checks content length limits (`src/content.test.js`, Node's built-in test runner).
- `npm run build` writes `dist/` (plus `404.html` for SPA deep links); `npm run preview` serves it at http://localhost:4173/ai-made-easy/.
- Pushes to `main` deploy to GitHub Pages via `.github/workflows/deploy-pages.yml`.

## Project structure

```
backend/
  app/
    api/        # HTTP routes
    services/   # business logic
    data/       # versioned roadmap/resource data (roadmap.v1.json)
    models.py   # Pydantic schemas
    config.py   # settings from .env
    main.py     # app factory
  tests/
frontend/
  src/          # React app
```
