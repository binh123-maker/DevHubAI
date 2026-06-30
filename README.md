# DevHub AI — MVP-8W Scaffold

Monorepo scaffold for DevHub AI MVP-8W: React frontend + FastAPI backend + PostgreSQL.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

| Service  | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health | http://localhost:8000/api/v1/health |

## Stack

**Frontend:** React, Vite, TypeScript, TailwindCSS, Shadcn UI (minimal), React Router, TanStack Query

**Backend:** FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, JWT (skeleton)

## Project Structure

```
DevHub/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/v1/   # API route stubs
│   │   ├── core/     # Config, security, dependencies
│   │   ├── db/       # Database session
│   │   ├── models/   # SQLAlchemy models (11 MVP tables)
│   │   └── schemas/  # Pydantic schemas
│   └── alembic/      # Database migrations
├── frontend/         # React application
│   └── src/
│       ├── api/      # Axios client
│       ├── components/
│       ├── contexts/ # Auth context skeleton
│       └── pages/    # 8 MVP pages
├── docs/             # Design documentation
└── docker-compose.yml
```

## Notes

- Business logic is **not implemented** — API endpoints return stubs or `501 Not Implemented`.
- Migrations run automatically on backend startup via `entrypoint.sh`.
- Design docs: see [docs/README.md](./docs/README.md).
