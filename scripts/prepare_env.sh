#!/usr/bin/env bash
set -euo pipefail

BIN_DIR=${BIN_DIR:-/usr/local/bin}
HELM_VERSION=${HELM_VERSION:-v3.16.3}
KUBECTL_VERSION=${KUBECTL_VERSION:-v1.31.3}
ARCH=${ARCH:-amd64}
OS=${OS:-linux}

need() {
  command -v "$1" >/dev/null 2>&1
}

install_helm() {
  echo "Installing helm ${HELM_VERSION}..."
  curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-${OS}-${ARCH}.tar.gz" -o /tmp/helm.tgz
  tar -xzf /tmp/helm.tgz -C /tmp
  install -m 0755 "/tmp/${OS}-${ARCH}/helm" "${BIN_DIR}/helm"
}

install_kubectl() {
  echo "Installing kubectl ${KUBECTL_VERSION}..."
  curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/${OS}/${ARCH}/kubectl" -o /tmp/kubectl
  install -m 0755 /tmp/kubectl "${BIN_DIR}/kubectl"
}

if ! need curl; then
  echo "curl is required" >&2
  exit 1
fi

if ! need helm; then
  install_helm
else
  echo "helm already installed: $(helm version --short 2>/dev/null || true)"
fi

if ! need kubectl; then
  install_kubectl
else
  echo "kubectl already installed: $(kubectl version --client 2>/dev/null | tr '\n' ' ')"
fi

echo "Tooling ready."
