# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full Stack FastAPI Template - a production-ready template with FastAPI backend and React frontend, including authentication (JWT), database (PostgreSQL), Docker deployment, and CI/CD.

## Development Commands

### Starting the Stack
```bash
docker compose watch
```

Access points:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer: http://localhost:8080
- Mailcatcher: http://localhost:1080
- Traefik UI: http://localhost:8090

### Backend Development
```bash
cd backend
uv sync                                    # Install dependencies
source .venv/bin/activate                   # Activate virtual env
fastapi dev app/main.py --reload            # Run dev server
```

Backend tests:
```bash
bash ./scripts/test.sh                      # Run all backend tests
docker compose exec backend bash scripts/tests-start.sh  # Run in container
```

Backend linting:
```bash
uv run ruff check                           # Lint
uv run ruff format                          # Format
uv run mypy                                 # Type check
uv run prek run --all-files                 # Run pre-commit hooks manually
```

### Frontend Development
```bash
cd frontend
bun install                                 # Install dependencies
bun run dev                                 # Run dev server (localhost:5173)
```

Frontend commands:
```bash
bun run build                               # Build for production
bun run lint                                # Format and lint (Biome)
bun run generate-client                     # Regenerate OpenAPI client
bunx playwright test                        # Run E2E tests
bunx playwright test --ui                   # E2E tests with UI
```

### Database Migrations
```bash
docker compose exec backend bash
alembic revision --autogenerate -m "Description"
alembic upgrade head                        # Apply migrations
```

### Generating Frontend API Client
After backend API changes:
```bash
bash ./scripts/generate-client.sh
```

## Architecture

### Backend Structure (`backend/app/`)
- `api/` - API endpoints (`deps.py`, `main.py`, `routes/`)
- `core/` - Core functionality (config, security, database)
- `models.py` - SQLModel schemas for database tables
- `crud.py` - CRUD operations for models
- `email-templates/` - MJML email templates (src/ → build/)
- `alembic/` - Database migrations

### Frontend Structure (`frontend/src/`)
- `client/` - Auto-generated OpenAPI client
- `components/` - Reusable UI components
- `hooks/` - Custom React hooks
- `routes/` - File-based routes (TanStack Router)
- `main.tsx` - Entry point

### Docker Compose Files
- `compose.yml` - Main stack configuration
- `compose.override.yml` - Development overrides (code volumes, hot reload)
- `compose.traefik.yml` - Traefik reverse proxy for production

### Package Managers
- Backend: `uv` (Python)
- Frontend: `bun` (Node.js)

## Key Technologies

**Backend**: FastAPI, SQLModel, PostgreSQL, Alembic, Pydantic, JWT, pytest
**Frontend**: React 19, TypeScript, Vite, TanStack Router, TanStack Query, Tailwind CSS, shadcn/ui, Playwright
**Infrastructure**: Docker, Docker Compose, Traefik

## Configuration

Environment variables in `.env` - change defaults before production:
- `SECRET_KEY` - Application secret
- `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD` - Admin credentials
- `POSTGRES_PASSWORD` - Database password
- `DOMAIN` - Production domain for Traefik

## Code Quality

- Pre-commit hooks: `prek` (modern alternative to pre-commit)
- Backend linting: ruff
- Frontend linting: Biome
- Type checking: mypy (backend), TypeScript (frontend)

Install pre-commit hooks:
```bash
cd backend && uv run prek install -f
```

## Important Notes

- Backend runs on port 8000, frontend on 5173 during development
- Docker Compose mounts source code as volumes for live reloading
- Email templates use MJML - convert to HTML in `build/` directory
- The `prestart` container runs Alembic migrations on startup
- Frontend uses file-based routing with TanStack Router (routeTree.gen.ts)
