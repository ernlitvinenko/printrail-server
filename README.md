# Printrail

> **The async backend for print-shop operations. Staff, roles, auth — and every database change leaves a trail.**

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.162+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/license-Elastic--2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ernlitvinenko/PrintCRM-server/actions/workflows/ci.yml/badge.svg)](https://github.com/ernlitvinenko/PrintCRM-server/actions/workflows/ci.yml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)

**Printrail** — self-hosted, async FastAPI backend for print shops and printing companies:
employee records, job positions, RBAC and JWT authentication — with **automatic, database-level
audit logging** out of the box. Every `INSERT` / `UPDATE` / `DELETE` on audited tables is captured
by PostgreSQL triggers into a JSONB snapshot log, with attribution of *who* made the change.

---

## ✨ Key Features

- 🖨 **Built for print shops** — domain models for employees, subsections (цеха/подразделения),
  job positions and contact info, plus accounts, roles and refresh tokens.
- 🔍 **Audit trail by default** — an Alembic post-migration hook auto-attaches PostgreSQL triggers
  to every table marked `has_audit_trigger`; before/after JSONB snapshots land in `audit_log`.
- 👤 **Per-user attribution** — the storage layer sets `app.current_user` via
  `set_config(...)` inside the transaction, so the audit trigger records the acting user.
- 🔐 **Production-grade auth skeleton** — JWT access/refresh token rotation, bcrypt password
  hashing, soft deletes (`is_del`) with an admin-only hard-delete path.
- 🧱 **Typed layered architecture** — `handlers → storage → models`, with a generic
  `_BaseStorage[T]` abstraction over SQLAlchemy 2.0 async sessions.
- 🗃 **SQLite & PostgreSQL** — driver is auto-selected from `DATABASE_URL`
  (`sqlite+aiosqlite` / `postgresql+asyncpg`).
- 🛠 **One CLI to run it all** — server, user bootstrap, dotenv and secret-key generation.

---

## 🚀 Quickstart

Requires **Python 3.12+** and [uv](https://docs.astral.sh/uv/).

```bash
# clone and install
git clone https://github.com/<you>/printrail.git
cd printrail
uv sync --all-groups

# generate .env and a JWT secret key
uv run main.py generate-dotenv
uv run main.py generate-secret-key   # paste into SECRET_KEY

# apply migrations (creates audit triggers automatically)
uv run alembic upgrade head

# create the first user
uv run main.py genuser

# run the server
uv run main.py runserver
```

The API is now at `http://0.0.0.0:8000` with OpenAPI docs at `/docs`.

---

## 🧰 CLI Commands

| Command | Description |
|---|---|
| `runserver` | Start uvicorn (hot-reload in `ENVIRONMENT=dev`) |
| `genuser` | Create an account with a generated password + bcrypt hash |
| `generate-dotenv` | Write a starter `.env` file |
| `generate-secret-key` | Generate a random JWT signing secret |

---

## ⚙️ Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | — | JWT signing secret (**required**) |
| `ENVIRONMENT` | `dev` | `dev` enables SQL echo and reload |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | SQLite or PostgreSQL DSN |
| `HOST` / `PORT` | `0.0.0.0` / `8000` | Bind address |
| `JWT_TOKEN_LIFETIME_MINUTES` | `15` | Access token TTL |
| `JWT_REFRESH_LIFETIME_DAYS` | `30` | Refresh token TTL |

See [`.env.sample`](.env.sample).

---

## 🏗 Architecture

```
core/
├── environment/      # pydantic-settings configuration (.env)
├── handlers/         # FastAPI routers (API v1: /api/auth/*)
├── helpers/          # bcrypt hashing, JWT utilities, datetime helpers
├── internal/         # async engine + session factory (asyncpg / aiosqlite)
├── models/
│   ├── database/     # SQLAlchemy 2.0 ORM models (Employee, Account, Role, AuditLog…)
│   └── requests/     # Pydantic request schemas
├── storage/          # typed repository layer, generic _BaseStorage[T]
└── scripts/          # CLI helpers (genuser, dotenv, secret key)
alembic/              # migrations + audit-trigger injection hook
```

### How the audit trail works

1. Every auditable model declares `{"info": {"has_audit_trigger": True}}` in `__table_args__`
   (via `ServiceFieldsMixin`).
2. On `alembic upgrade head`, a custom `process_revision_directives` hook detects newly created
   audited tables and appends `CREATE TRIGGER trg_audit_<table> AFTER INSERT OR UPDATE OR DELETE`
   statements — and the matching `DROP TRIGGER` to the downgrade path.
3. Each trigger calls `process_audit_log()`, writing old/new row snapshots (JSONB), action type,
   row id and `changed_by` (read from the `app.current_user` transaction setting that the
   storage layer sets on every write) into `audit_log`.

No application code needs to remember to log — the database enforces it.

---

## 🧪 Testing

```bash
uv sync --all-groups        # installs pytest, pytest-asyncio, aiosqlite, httpx
uv run pytest -v
```

Tests run against **in-memory SQLite** — no external services required. The suite covers:

- JWT creation/verification (incl. expiry rejection)
- bcrypt password hashing
- Storage layer CRUD, soft/hard delete semantics and kwargs validation
- Alembic audit-trigger generation logic
- API routing smoke tests (routes registered, OpenAPI schema intact)

CI (`.github/workflows/ci.yml`) runs on every push/PR:

1. **Lint** — `ruff check` + `ruff format --check`
2. **Secrets** — gitleaks scan of the full history
3. **Tests** — pytest matrix over Python 3.12/3.13 × SQLite/PostgreSQL (with Alembic migrations applied against the real Postgres service)

---

## 🔭 Roadmap

- [ ] Implement `/auth/token`, `/auth/refresh`, `/auth/me` endpoints (JWT rotation)
- [ ] Role-based access control (RBAC) on handlers
- [ ] Audit log read API (`GET /audit`)
- [ ] Print-shop domain: orders, job tickets, materials
- [ ] Docker Compose for one-command PostgreSQL deployment
- [ ] Test suite (pytest + async SQLAlchemy fixtures)

---

## 🤝 Contributing

```bash
uv sync --all-groups
uv run pre-commit install   # ruff lint + format on commit
```

## 📄 License

Distributed under the [Elastic License 2.0 (ELv2)](LICENSE).

You may use, copy, and modify the software freely, **including in production and commercial
environments**, but you may **not provide it to others as a managed service** (i.e. host it,
wrap it, and sell access to it). See the [license text](LICENSE) for the three simple limits
and the full terms.
