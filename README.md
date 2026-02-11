# Private ResumeOps Platform

A full-stack, end-to-end platform for:

- Generating targeted resumes from a master profile.
- Scoring open jobs against a generated resume.
- Automatically preparing and submitting job applications.
- Deploying with private networking where APIs are never publicly exposed.

## Architecture

- **Frontend**: Lightweight SPA (`frontend/`) for resume/job workflows.
- **Backend API**: FastAPI service (`backend/`) exposing internal-only `/api/*` endpoints.
- **Worker**: Background worker (`worker/`) that continuously polls and submits queued applications.
- **Data Stores**:
  - PostgreSQL for persisted profiles/resumes/jobs.
  - Redis for application queueing.
- **Deployment**:
  - Docker Compose for local E2E.
  - Helm chart (`helm/resume-ops`) for Kubernetes with:
    - ClusterIP services for API/worker dependencies.
    - private ingress for UI only.
    - NetworkPolicy restricting traffic paths.

## Local run (Docker Compose)

```bash
docker compose up --build
```

Then open: `http://localhost:8080`

> API is not directly published; frontend proxies `/api` traffic over private network to backend.

## Local run (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Serve frontend separately (for quick development):

```bash
python -m http.server 8080 --directory frontend
```

## Example flow

1. Create a profile in the UI.
2. Generate a role-specific resume.
3. Paste jobs into UI and queue auto-apply.
4. Worker consumes queue and simulates ATS submissions.

## Helm deployment

```bash
helm upgrade --install resume-ops ./helm/resume-ops -n resume-ops --create-namespace
```

### Private networking defaults

- Backend/API service is `ClusterIP` only.
- No ingress is defined for API.
- Frontend ingress is configured for private ingress class by default.
- NetworkPolicy enforces only approved east-west traffic.

