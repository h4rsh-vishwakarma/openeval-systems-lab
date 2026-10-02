# Security design and limitations

- Synthetic fixtures only; no production or employer material.
- `.env`, private keys, Terraform state, build output, and Parquet are ignored by Git. Check `git status` before any public push.
- The API requires a bearer token for task routes; health is unauthenticated. `API_TOKENS_JSON` optionally maps separate tenant IDs to tokens and all task queries are tenant scoped. This is a demo substitute for user identity. Input is validated with Pydantic, TypeScript with Zod, and request bodies are limited in the gateway.
- Rate limiting uses Redis per apparent client IP with 120 requests per minute. Behind Nginx this is a shared proxy IP, so it is a coarse demo safeguard.
- Database queries use SQLAlchemy parameters. React renders strings as text. No submitted code is executed.
- PostgreSQL and Redis have no host ports. The Python API and TypeScript gateway bind to loopback host ports in Compose. Only the client port is public.
- The supplied EC2 configuration is a demo scaffold. Add TLS, identity management, secret storage, backups, vulnerability scanning, and network review before real internet use.
