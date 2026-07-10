# SaaS Starter Kit — Multi-Tenant Auth & Permissions

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688)
![React](https://img.shields.io/badge/React-18-61DAFB)
![License](https://img.shields.io/badge/License-MIT-green)

A starter kit for building **multi-tenant SaaS applications** with **FastAPI**, **React**, JWT authentication, organization-based access control, invitations, and tenant isolation.

---

## ✨ Features

- ✅ JWT Authentication
- ✅ User Registration & Login
- ✅ Multi-Tenant Architecture
- ✅ Organization Management
- ✅ Membership Management
- ✅ Invite Users to Organizations
- ✅ Tenant Data Isolation
- ✅ Role-Based Access Control (RBAC)
- ✅ Audit Events for Key Actions
- ✅ Async SQLAlchemy
- ✅ Alembic Database Migrations
- ✅ Docker & Docker Compose
- ✅ React + Vite Frontend

---

## 🧠 Design Decisions

### Tenant isolation strategy
This starter adopts a shared-database approach with explicit organization context and membership checks. It is a practical default for early-stage SaaS products because it keeps the system simpler to build, operate, and evolve while still enforcing tenant boundaries. A future step could be moving to schema-per-tenant or database-per-tenant if the product grows.

### RBAC model
The access model currently uses roles such as owner, admin, and member. This is a more realistic foundation than a single fixed role because it allows the product to express different levels of operational authority inside an organization.

### Invite flow
Invites are issued as short-lived tokens, validated on acceptance, and tied to organization membership. This creates a safer onboarding flow than a simple open join mechanism and makes the invitation lifecycle easier to reason about.

### Security and testing
The backend includes regression tests for cross-tenant access, authorization failures, invite expiration, and audit event creation. These tests are meant to show that tenant boundaries are not just implemented, but actively protected.

---

## 📸 Preview

![SaaS Starter preview](assets/screenshot.png)

---

## 🛠 Tech Stack

### Backend

- FastAPI
- SQLAlchemy 2.0 (Async)
- Pydantic
- Alembic
- JWT Authentication
- Passlib (Password Hashing)

### Frontend

- React
- Vite

### Database

- SQLite (development)
- Ready for PostgreSQL

### DevOps

- Docker
- Docker Compose

---

## 📁 Project Structure

```
backend/
    app/
    tests/
    Dockerfile

frontend/
docker-compose.yml
README.md
```

---

## 🚀 Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
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

---

## 🔑 Demo Credentials

```
Email: demo@example.com
Password: secret123
```

---

## 🧪 Running Tests

```bash
cd backend
pytest
```

---

## 🗺 Roadmap

- PostgreSQL support
- Complete Alembic migrations
- CI/CD with GitHub Actions
- Automated tests expansion
- Billing module
- Admin dashboard
- Organization roles & permissions
- Email invitation workflow
- Production deployment

---

## 📌 About

This project was created as a practical foundation for building **modern multi-tenant SaaS applications**. It demonstrates concepts commonly used in production systems, including authentication, tenant isolation, organization management, invitations, and scalable backend architecture.