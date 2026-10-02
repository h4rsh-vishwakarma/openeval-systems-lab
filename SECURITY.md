# Security policy

This repository uses synthetic fixtures. Do not commit tokens, private keys, credentials, employer information, or proprietary code. Report security issues privately to the repository owner; do not open an issue containing exploit details or secrets.

Gitleaks directory scan completed on 2026-10-02 with no findings. CI repeats the scan on each push and pull request.

The local bearer token is a demo control, not production identity management. For an internet deployment, put the client behind HTTPS, store secrets in a managed secret store, add individual user authentication and tenant authorization, restrict database and Redis to private networking, and review dependency and container updates. See [security design](docs/SECURITY.md).
