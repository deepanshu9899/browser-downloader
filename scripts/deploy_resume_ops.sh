#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${NAMESPACE:-resume-ops}
RELEASE=${RELEASE:-resume-ops}
CHART=${CHART:-./helm/resume-ops}
INGRESS_CLASS=${INGRESS_CLASS:-nginx}
INGRESS_HOST=${INGRESS_HOST:-}
PUBLIC=${PUBLIC:-false}

command -v kubectl >/dev/null 2>&1 || { echo "kubectl not found" >&2; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "helm not found" >&2; exit 1; }

kubectl get ns "${NAMESPACE}" >/dev/null 2>&1 || kubectl create ns "${NAMESPACE}"

if [[ "${PUBLIC}" == "true" ]]; then
  if [[ -z "${INGRESS_HOST}" ]]; then
    echo "PUBLIC=true requires INGRESS_HOST" >&2
    exit 1
  fi

  helm upgrade --install "${RELEASE}" "${CHART}" \
    -n "${NAMESPACE}" \
    --set frontend.ingress.className="${INGRESS_CLASS}" \
    --set frontend.ingress.host="${INGRESS_HOST}" \
    --set frontend.ingress.annotations.nginx\.ingress\.kubernetes\.io/whitelist-source-range=0.0.0.0/0
else
  helm upgrade --install "${RELEASE}" "${CHART}" -n "${NAMESPACE}"
fi

kubectl rollout status deploy/${RELEASE}-resume-ops-frontend -n "${NAMESPACE}" --timeout=180s
kubectl rollout status deploy/${RELEASE}-resume-ops-backend -n "${NAMESPACE}" --timeout=180s
kubectl rollout status deploy/${RELEASE}-resume-ops-worker -n "${NAMESPACE}" --timeout=180s

if [[ "${PUBLIC}" == "true" ]]; then
  echo "Frontend URL: http://${INGRESS_HOST}"
else
  echo "Private deployment completed."
fi
