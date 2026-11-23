# AI Made Easy

*Learn how to use AI, step by step — free, no jargon.*

Helping everyday people learn to get real work done with ChatGPT, Claude, Gemini, Copilot and other AI assistants. Every stage teaches through a hands-on example, and links go to curated, verified resources. There are two tracks:

- **Use AI Assistants** (default): for everyone, no coding. Covers setting up your assistant, prompting, files and Projects, apps and connectors, MCP, skills and custom GPTs, agents, safety, and workflows.
- **Build with AI (for developers)**: model APIs, retrieval (RAG), tools and agents, evaluation, and shipping AI apps. *Hidden for now; see `ENABLED_TRACKS` below.*

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
python -m app   # host/port come from .env (APP_HOST / APP_PORT); auto-reloads on .py and app/data/*.json changes
```

- Health check: http://127.0.0.1:8001/api/health
- API docs: http://127.0.0.1:8001/docs
- Tests: `pytest`

Config (`backend/.env`): `APP_HOST`, `APP_PORT`, `CORS_ORIGINS` (comma-separated), `DATA_FILE`, `ENABLED_TRACKS`.
Default port is 8001 (8000 is often taken on Windows). If you change it, update `VITE_API_BASE_URL` in `frontend/.env` too.

**Tracks shown:** `ENABLED_TRACKS` (comma-separated, default `use`) controls which tracks the API exposes. The Build track is currently hidden: its data stays in the JSON file, but `/api/tracks`, `/api/stages` and `/api/resources` leave it out, and its mind map and stage ids return `404`. To re-enable it, set `ENABLED_TRACKS=use,build` in `backend/.env` and restart the backend. Unknown track ids in this setting stop the server from starting.

### API

| Endpoint | Description |
| --- | --- |
| `GET /api/health` | Health check |
| `GET /api/tracks` | `[{id, title, description, stage_count}]`, `use` first |
| `GET /api/tracks/{id}/mindmap` | Mind-map tree: `{track: {id, title, description}, stages: [{id, title, icon, color, takeaway, example: {title}, topics: [{title, takeaway, example}]}]}`. `404` if the track is unknown or disabled |
| `GET /api/stages?track=` | Stage summaries ordered by track then `order`; all tracks if `track` is omitted. Each has `track`, `takeaway`, `icon`, `color`, `topics`, `resource_count` (no `goals`/`example`/`resources`) |
| `GET /api/stages/{id}` | Full stage, including `goals`, `example` and `resources`; `404` if unknown |
| `GET /api/resources?track=&level=&type=&cost=&q=` | All resources (each with `track`, `stage_id`, `stage_title`), filtered. `track`: use/build; `level`: beginner/intermediate/advanced; `type`: docs/course/video/article/tool/repo; `cost`: free/paid; `q`: case-insensitive search over title, description, provider (max 100 chars) |

Invalid query values (`track`, `level`, `type`, `cost`) return `422`. A `track` that is unknown or disabled is rejected the same way (`422`, listing the enabled tracks). In the mindmap path, an unknown or disabled track returns `404`, because there it identifies a resource.

### Roadmap data

All content lives in `backend/app/data/roadmap.v2.json`, selected by `DATA_FILE`. It's versioned through its `version`/`updated` fields: 2.0.0 added tracks, takeaways, icons, colours and topic objects; 2.1.0 rebuilt the Use track and added hands-on examples. The file is validated against the Pydantic models in `app/models.py` on load. Loading fails if any of these rules is broken:

- track, stage and resource ids are unique (stage ids across all tracks)
- `(track, order)` pairs are unique
- every stage references a defined track
- stage and topic `takeaway`s are 12 words or fewer
- `color` is a `#RRGGBB` hex value
- every stage has an `example` with at least one step, and every topic has an `example`

Stage shape (detail endpoint):

```text
{id, track, order, title, summary, takeaway, icon, color, level, estimated_time, goals: [str],
 topics: [{title, takeaway, example}],              # example = one concrete usage line
 example: {title, scenario, steps: [str],           # required hands-on walkthrough
           prompt: str | null,                      # copy-paste prompt
           code: {language, content} | null,        # config or snippet, e.g. MCP JSON
           expected_result},
 resources: [{id, title, url, provider, type, level, cost, description}]}
```

Tests also check that every stage colour has WCAG AA contrast (≥ 4.5:1) with white text, and that every Use-track stage has 3-6 resources, a prompt or code to try, and topic examples. `icon` is an optional single emoji. Edit the JSON and restart the server to update content.

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
    data/       # versioned roadmap/resource data (roadmap.v2.json)
    models.py   # Pydantic schemas
    config.py   # settings from .env
    main.py     # app factory
  tests/
frontend/
  src/          # React app
```
