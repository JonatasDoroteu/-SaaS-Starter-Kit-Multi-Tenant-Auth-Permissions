# SaaS Starter Kit — Multi-Tenant Auth & Permissions

Um starter para aplicações SaaS multi-tenant, com foco em autenticação, isolamento de dados entre organizações e controle de acesso baseado em papéis (RBAC).

O objetivo é construir uma base sólida usando conceitos presentes em aplicações SaaS modernas — arquitetura organizada, segura e preparada para evoluir.

> 🚧 Projeto em desenvolvimento ativo. Feedbacks e sugestões são sempre bem-vindos!

📸 Preview 
## Login

![Login](screenshots/login.png)

## Dashboard

![Dashboard](screenshots/dashboard.png)

## ✅ O que o projeto já oferece

- Arquitetura multi-tenant com isolamento de dados por organização
- Autenticação segura utilizando JWT (access token de vida curta + refresh token opaco e revogável)
- Backend assíncrono com **FastAPI** + **SQLAlchemy 2.0 (Async)**
- Frontend desenvolvido com **React** + **Vite**
- Gerenciamento de organizações, memberships e convites de usuários
- Sistema de convites com:
  - token único
  - expiração
  - validação e aceite do convite
- Controle de acesso baseado em papéis (RBAC):
  - `Owner`
  - `Admin`
  - `Member`
- Administradores podem convidar novos membros
- Auditoria básica registrando eventos como:
  - criação de organizações
  - criação de convites
  - aceite de convites

---

## 🔎 Evidência verificada

A suíte de testes do backend foi executada com sucesso:

```bash
pytest -q
```

**Resultado:** ✅ 9 testes passaram

Os testes validam os principais fluxos implementados, incluindo:
- isolamento de dados entre organizações
- regras de autorização por role
- criação e aceitação de convites

---

## 🛠️ Stack utilizada

**Backend**
- Python
- FastAPI
- SQLAlchemy 2.0 (Async)
- JWT (`python-jose`)
- Pytest
- Alembic (migrations)
- SQLite (desenvolvimento)

**Frontend**
- React
- Vite

---

## 📂 Estrutura do projeto

```
.
├── backend/
│   ├── app/
│   │   ├── api/routes/       # endpoints (auth, organizations, invites, health)
│   │   ├── core/             # config e segurança (JWT, hashing)
│   │   ├── models/           # models SQLAlchemy (User, Organization, Membership, Invite, ...)
│   │   ├── schemas/          # schemas Pydantic
│   │   ├── services/         # regras de negócio e acesso a dados
│   │   └── main.py
│   ├── alembic/ / migrations/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/                  # App React + Vite
│   ├── index.html
│   └── package.json
└── docker-compose.yml
```

---

## 🚀 Rodando localmente

### Pré-requisitos
- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/Mac

pip install -r requirements.txt
uvicorn app.main:app --reload
```

O backend sobe em `http://127.0.0.1:8000`. Documentação interativa (Swagger) disponível em `http://127.0.0.1:8000/docs`.

Um usuário de demonstração é criado automaticamente ao iniciar o servidor:

```
email: demo@example.com
senha: secret123
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O frontend sobe em `http://localhost:3000`.

> ⚠️ Backend e frontend precisam estar rodando **ao mesmo tempo**, em terminais separados. O CORS já está configurado para aceitar requisições vindas de `http://localhost:3000`.

### Testes

```bash
cd backend
pytest -q
```

---

## 🔹 Próximos passos

- [ ] Migração para PostgreSQL em produção
- [ ] Docker e Docker Compose completos
- [ ] Pipeline de CI/CD com GitHub Actions
- [ ] Expansão da cobertura de testes
- [ ] Sistema de permissões mais granular, independente das roles
- [ ] Evolução do sistema de convites (reenvio, recusa, notificações por e-mail e histórico)
- [ ] Auditoria mais robusta e consultável

---

## 🧠 Sobre o projeto

O projeto ainda está em desenvolvimento, mas já evoluiu para uma base próxima da arquitetura utilizada em aplicações SaaS reais, explorando conceitos como multi-tenancy, autenticação, autorização e boas práticas de backend.

---

`#Python` `#FastAPI` `#React` `#Vite` `#SQLAlchemy` `#JWT` `#RBAC` `#SaaS` `#Backend` `#SoftwareEngineering` `#APIs` `#MultiTenant` `#Docker` `#PostgreSQL` `#GitHub` `#OpenSource` `#WebDevelopment`