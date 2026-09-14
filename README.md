# CivicGuard

Civic incident reporting platform for India. Citizens upload video or photos; the system runs behavior detection and AI triage, then routes cases to police, municipal teams, or human review.

This repository is a **skeleton**. Detection, triage, case workflows, and the admin dashboard are not implemented yet.

## Stack

- Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- PyTorch, Ultralytics YOLOv10, OpenCV, RetinaFace
- Anthropic Claude (`claude-sonnet-4-6`) for triage
- JWT auth
- Local filesystem uploads (S3 later)
- Admin dashboard: HTML + Tailwind CSS

## Project layout

```
civicguard/
├── main.py                 # FastAPI entrypoint (`uvicorn main:app`)
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── app/                    # API, config, models, schemas, services
├── detection/              # YOLOv10 civic-offense detection (placeholder)
├── triage/                 # Claude classification (placeholder)
├── cases/                  # Case IDs, status, citizen notify (placeholder)
├── dashboard/              # Reviewer web UI (placeholder)
├── uploads/                # Local media storage
└── tests/
```

## Local setup

1. **Python 3.11** (project target; Docker uses 3.11) and optional **Docker Desktop**. If 3.11 is not installed locally, use 3.13 for the skeleton API (`py -3.13`). Full ML packages (PyTorch, Ultralytics) are easiest on 3.11 or 3.13.

2. Create a virtual environment and install dependencies:

   ```powershell
   cd C:\Users\ajayg\Projects\civicguard
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   For a minimal health-check run only (no ML/DB yet):

   ```powershell
   pip install "fastapi==0.141.1" "uvicorn[standard]==0.52.4"
   ```

   On macOS/Linux:

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copy environment variables:

   ```powershell
   copy .env.example .env
   ```

   Set `ANTHROPIC_API_KEY` and a strong `JWT_SECRET` before enabling triage or auth.

4. Start PostgreSQL (Docker) if you need a database:

   ```powershell
   docker compose up db -d
   ```

   The API health check does **not** require Postgres.

5. Run the API:

   ```powershell
   uvicorn main:app --reload
   ```

6. Check health:

   - Browser or curl: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
   - Expected JSON: `{"status":"ok","service":"CivicGuard"}`
   - Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Docker (API + Postgres)

```powershell
copy .env.example .env
docker compose up --build
```

- API: http://127.0.0.1:8000/health
- Postgres: `localhost:5432` (user/password/db: `civicguard`)

The first image build installs PyTorch and other ML packages and can take several minutes.

## Planned modules

| Component | Path | Role |
| --- | --- | --- |
| Behavior detection | `detection/` | YOLOv10 on frames: littering, dumping, fighting, vandalism |
| AI triage | `triage/` | Claude: `URGENT`, `CIVIC`, `LOW_CONFIDENCE` |
| Case management | `cases/` | Case IDs, status, citizen notifications |
| Admin dashboard | `dashboard/` | Human review of incoming reports |

## License

Proprietary / to be decided.
