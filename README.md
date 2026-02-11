# ResumeOps Platform

A full-stack, end-to-end platform for:

- Generating targeted resumes from a master profile.
- Scoring open jobs against a generated resume.
- Automatically preparing and submitting job applications.
- Deploying with Kubernetes + Helm.

## Architecture

- **Frontend**: Lightweight SPA (`frontend/`) for resume/job workflows.
- **Backend API**: FastAPI service (`backend/`) exposing `/api/*` endpoints (proxied by frontend).
- **Worker**: Background worker (`worker/`) that continuously polls and submits queued applications.
- **Data Stores**:
  - PostgreSQL for persisted profiles/resumes/jobs (future extension).
  - Redis for application queueing.
- **Deployment**:
  - Docker Compose for local E2E.
  - Helm chart (`helm/resume-ops`) for Kubernetes.

## Local run (Docker Compose)

```bash
docker compose up --build
```

Then open: `http://localhost:8080`

## Example flow

1. Create a profile in the UI.
2. Generate a role-specific resume.
3. Paste jobs into UI and queue auto-apply.
4. Worker consumes queue and simulates ATS submissions.

## Helm deployment

```bash
helm upgrade --install resume-ops ./helm/resume-ops -n resume-ops --create-namespace
```

### Public URL configuration

To expose the app with a public URL, configure the frontend ingress host:

```bash
helm upgrade --install resume-ops ./helm/resume-ops \
  -n resume-ops --create-namespace \
  --set frontend.ingress.enabled=true \
  --set frontend.ingress.className=nginx \
  --set frontend.ingress.host=resume-ops.example.com
```

If you do not have DNS yet, you can use `nip.io` with your ingress external IP:

```bash
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
helm upgrade --install resume-ops ./helm/resume-ops \
  -n resume-ops --create-namespace \
  --set frontend.ingress.host=resume-ops.${INGRESS_IP}.nip.io
```

Then access:

- `http://resume-ops.<INGRESS_IP>.nip.io`

### Optional TLS

Enable TLS after creating a certificate secret:

```bash
kubectl create secret tls resume-ops-tls -n resume-ops --cert=tls.crt --key=tls.key
helm upgrade --install resume-ops ./helm/resume-ops \
  -n resume-ops \
  --set frontend.ingress.tls.enabled=true \
  --set frontend.ingress.tls.secretName=resume-ops-tls
```

