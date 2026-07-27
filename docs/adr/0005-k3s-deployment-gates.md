# ADR 0005: K3S deployment gates and two-repository contract

- Status: Accepted
- Date: 2026-07-27

## Context

`gabrielWYP/K3S_Infra` uses a two-repository release model. An application
workflow builds immutable GHCR images after CI and calls a reusable workflow in
the infrastructure repository. The infrastructure workflow validates
manifests, reconciles Kubernetes secrets, applies Kustomize, waits for rollout,
and verifies internal and public health.

C1 is primarily a batch data and evaluation milestone. Deploying a public
service before a forecast API exists would add operational surface without a
stable user-facing capability.

## Decision

MarketPulse has two deployment gates:

1. **Internal data deployment — after C1 plus packaging.** Deploy the hourly
   ingestion/materialization workload without public Ingress after adding an
   immutable non-root image, remote MinIO credentials, a scheduler/runtime, and
   K3S manifests. This proves persistence, backfill, freshness metrics, and
   restart behavior in the real cluster.
2. **Public application deployment — C3.** Add Traefik routing only when health,
   readiness, `/metrics`, `/forecasts`, and `/models` exist and the champion is
   running in shadow/paper mode.

The application caller will run only after successful CI on `main`, build an
immutable multi-architecture GHCR image, and call:

```yaml
uses: gabrielwyp/K3S_Infra/.github/workflows/deploy-marketpulse.yml@main
```

The reusable workflow and Kustomize manifests remain owned by `K3S_Infra`.
Cluster access and runtime credentials remain GitHub Actions Secrets and are
never committed. No deployment workflow may enable real orders.

## Consequences

- C1 can be deployed internally, but that deployment is not the public MVP.
- C3 is the first economically meaningful public deployment gate.
- MarketPulse and K3S infrastructure changes should use separate reviewed PRs.
- A successful application CI run is necessary but not sufficient: rollout,
  storage write/read, metrics freshness, and smoke checks must also pass.
