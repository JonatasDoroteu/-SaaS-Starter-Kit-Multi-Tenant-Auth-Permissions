# SaaS Starter — Multi-Tenant Auth & Permissions

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688)
![React](https://img.shields.io/badge/React-18-61DAFB)
![License](https://img.shields.io/badge/License-MIT-green)

A practical starter for building multi-tenant SaaS applications with FastAPI, JWT authentication, organization-based access control, invites, and a simple React frontend.

## Why this project exists

This starter focuses on the core foundation of a SaaS product: authentication, tenant boundaries, organization membership, and invite-based onboarding. It is designed to be a strong starting point for building products that need multi-tenant isolation from day one.

## What this project includes

- FastAPI backend
- JWT-based authentication and password hashing
- Organization and membership model
- Tenant-aware access control with organization headers
- Invite flow for onboarding members
- React + Vite frontend starter
- Alembic scaffolding for database migrations
- Docker support for local containerized runs

## Tech stack

- Backend: FastAPI, SQLAlchemy async, Pydantic, Alembic
- Auth: JWT, Passlib
- Frontend: React, Vite
- Database: SQLite by default, ready for Postgres-style adaptation
- Containerization: Docker / Docker Compose

## Project structure

- backend/: FastAPI app, models, routes, services, tests
- frontend/: React/Vite client
- docker-compose.yml: local container run configuration

## Run locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 3000
```

### Docker

```bash
docker compose up --build
```

## Demo credentials

- Email: demo@example.com
- Password: secret123

## Tests

```bash
cd backend
pytest -q
```

## Roadmap

- Add PostgreSQL support via Docker Compose
- Generate and apply real Alembic migrations
- Strengthen tenant enforcement with a shared dependency layer
- Add billing, roles, and admin dashboards
- Improve frontend experience for invite and organization management

## Notes

This starter focuses on the core SaaS foundation: authentication, tenant boundaries, organization membership, and invite-based onboarding.
