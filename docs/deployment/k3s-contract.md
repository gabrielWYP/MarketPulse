# K3S deployment contract

## Observed platform pattern

The application repository owns source CI, immutable image publication, and
the caller workflow. `gabrielWYP/K3S_Infra` owns reusable deploy workflows,
Kustomize manifests, secret reconciliation, cluster access, rollout checks, and
public routing.

The MarketPulse caller should mirror the proven pattern:

```text
CI on main
  -> select immutable source SHA
  -> build linux/amd64 and linux/arm64 image
  -> push ghcr.io/gabrielwyp/marketpulse:<main-SHA>
  -> call K3S_Infra/.github/workflows/deploy-marketpulse.yml@main
```

## Internal C1 deployment inputs

- immutable image tag;
- namespace `marketpulse`;
- `KUBECONFIG_B64` and `GHCR_PULL_TOKEN`;
- MinIO endpoint, bucket, access key, and secret key;
- paper-trading and real-order flags fixed to `true` and `false` respectively.

The first workload should have no Ingress. Its acceptance checks are successful
raw write/read, idempotent replay, Dagster materialization, freshness metrics,
resource limits, and retry-safe restart.

## Public C3 deployment inputs

C3 adds a Service and Traefik IngressRoute only after `/health`, `/ready`,
`/metrics`, `/forecasts`, and `/models` are implemented. Public smoke checks
must verify payload semantics, not only HTTP status.
