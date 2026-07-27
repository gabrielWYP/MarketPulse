# Security policy

## Reporting

Do not open a public issue containing a credential, exploit, or sensitive
deployment detail. Contact the repository owner privately and include only the
minimum evidence needed to reproduce the issue.

## Credential boundary

- Never commit `.env`, API keys, private keys, cloud credentials, or Terraform
  state.
- Use GitHub Actions Secrets or OpenID Connect for CI/CD.
- Use AWS Secrets Manager and workload identity for runtime access.
- Public market-data ingestion must work without a Binance API key.
- MarketPulse is paper-trading only. The codebase must reject configuration
  that attempts to enable real-order execution.

If a secret is exposed, revoke it immediately, remove it from active systems,
and treat Git history rewriting as cleanup rather than revocation.
