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
    - private ingress for UI by default.
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


## Environment preparation

Use the helper script to install deployment tooling (`helm`, `kubectl`):

```bash
./scripts/prepare_env.sh
```

Then deploy:

```bash
./scripts/deploy_resume_ops.sh
```

Public frontend URL deploy:

```bash
PUBLIC=true INGRESS_HOST=resume-ops.example.com ./scripts/deploy_resume_ops.sh
```

## Helm deployment

```bash
helm upgrade --install resume-ops ./helm/resume-ops -n resume-ops --create-namespace
```

### Private networking defaults

- Backend/API service is `ClusterIP` only.
- No ingress is defined for API.
- Frontend ingress defaults to private class/host settings.
- NetworkPolicy enforces approved east-west traffic only.

### Optional public URL for frontend

If you want a public URL for the **frontend only** (API still private behind frontend proxy), override ingress values:

```bash
helm upgrade --install resume-ops ./helm/resume-ops \
  -n resume-ops --create-namespace \
  --set frontend.ingress.enabled=true \
  --set frontend.ingress.className=nginx \
  --set frontend.ingress.host=resume-ops.example.com \
  --set frontend.ingress.annotations.nginx\.ingress\.kubernetes\.io/whitelist-source-range=0.0.0.0/0
```

If you do not have DNS yet, use `nip.io` with your ingress external IP:

```bash
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
helm upgrade --install resume-ops ./helm/resume-ops \
  -n resume-ops --create-namespace \
  --set frontend.ingress.className=nginx \
  --set frontend.ingress.host=resume-ops.${INGRESS_IP}.nip.io \
  --set frontend.ingress.annotations.nginx\.ingress\.kubernetes\.io/whitelist-source-range=0.0.0.0/0
```

### Optional TLS

```bash
kubectl create secret tls resume-ops-tls -n resume-ops --cert=tls.crt --key=tls.key
helm upgrade --install resume-ops ./helm/resume-ops \
  -n resume-ops \
  --set frontend.ingress.tls.enabled=true \
  --set frontend.ingress.tls.secretName=resume-ops-tls
```
