# ADR 0004: Secrets never enter Git

- Status: Accepted
- Date: 2026-07-27

## Context

MarketPulse is a public repository. Removing a leaked credential from the latest
commit does not revoke it or guarantee removal from history and caches.

## Decision

- Local values live in ignored `.env` files.
- `.env.example` contains placeholders only.
- GitHub Actions uses repository/environment secrets or OpenID Connect.
- AWS workloads use Secrets Manager and workload identity such as IRSA.
- Terraform state, private keys, API keys, and Office source binaries are
  ignored.

## Consequences

Secret scanning runs locally and in CI. Any exposure triggers immediate
revocation; history cleanup is not treated as a substitute for rotation.
