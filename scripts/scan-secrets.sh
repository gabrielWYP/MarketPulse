#!/usr/bin/env bash
set -euo pipefail

readonly pattern='(AKIA[0-9A-Z]{16}|gh[opurs]_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'

if git grep -n -I -E "${pattern}" -- ':!scripts/scan-secrets.sh'; then
  printf '{"event":"secret_scan","status":"failed"}\n' >&2
  exit 1
fi

printf '{"event":"secret_scan","status":"passed"}\n'
