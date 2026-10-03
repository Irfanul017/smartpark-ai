# SmartPark AI

An explainable intelligent parking-slot allocation system. SmartPark AI uses a Python fuzzy inference engine to score compatible, available slots by distance, congestion, compatibility, walking distance, and user priority.

## Structure

```text
smartpark-ai/
├── backend/       # FastAPI API and tests
├── frontend/      # React + Vite + TypeScript client
├── docs/          # Project documentation
└── PROJECT_CONTEXT.md
```

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer with a working npm installation

## Backend setup

Run from the `smartpark-ai` directory:

```powershell
py -3.11 -m venv backend/.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

The API runs on `http://127.0.0.1:8000`. Visit `/` for the project status, `/health` for a health check, and `/docs` for Swagger UI.

Run backend tests after activating the virtual environment:

```powershell
pytest backend/tests
```

## Frontend setup

In a second terminal from `smartpark-ai`:

```powershell
Set-Location frontend
npm install
npm run dev
```

Vite serves the client at `http://localhost:5173`. The Home page calls `http://localhost:8000/health`; start the backend first to see its healthy status.

## Demo data

Seed the complete A01–D05 interactive parking lot and local administrator:

```powershell
Set-Location backend
python -m app.seed_demo_data
```

The development administrator is `admin` / `Admin@12345`. Change the password and set `SMARTPARK_JWT_SECRET` before using this outside a local demo.

## Main endpoints

| Endpoint | Response |
| --- | --- |
| `GET /` | `{ "project": "SmartPark AI", "status": "running" }` |
| `GET /health` | `{ "status": "healthy" }` |
| `POST /api/auth/register` | Create an account |
| `POST /api/auth/login` | Get a JWT access token |
| `GET /api/parking/slots` | List live parking slots |
| `POST /api/parking/recommend` | Receive top 3 fuzzy-ranked recommendations |
| `POST /api/parking/allocate` | Allocate a selected slot |
| `POST /api/ai/calculate-score` | Calculate a standalone fuzzy score |

Development CORS is enabled for `localhost:5173` and `127.0.0.1:5173`.
