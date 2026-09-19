# SaaS Starter Kit — Multi-Tenant Auth & Permissions

![CI](https://github.com/JonatasDoroteu/-SaaS-Starter-Kit-Multi-Tenant-Auth-Permissions/actions/workflows/ci.yml/badge.svg)

Um starter para aplicações SaaS multi-tenant, com foco em autenticação, isolamento de dados entre organizações, controle de acesso baseado em papéis (RBAC), cotas de uso por plano e emissão segura de chaves de API.

O objetivo é construir uma base sólida usando conceitos presentes em aplicações SaaS modernas — arquitetura organizada, segura e preparada para evoluir.

> Projeto em desenvolvimento ativo. Feedbacks e sugestões são sempre bem-vindos!

## 🔗 Demo ao vivo

- **API em produção:** https://saas-starter-kit-multi-tenant-auth.onrender.com
- **Documentação interativa (Swagger):** https://saas-starter-kit-multi-tenant-auth.onrender.com/docs
- Backend rodando no **Render**, banco **PostgreSQL** gerenciado pelo **Supabase**.
- Plano gratuito: a API "dorme" após período de inatividade — a primeira requisição pode levar ~30-50s pra responder.

📸 Preview

## Login

![login](screenshots/login.png)

## Dashboard

![Dashboard](screenshots/dashboard.png)

## Usage & Quotas

![Usage](screenshots/usage.png)

## API Keys

![API Keys](screenshots/api.png)

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
- **Cotas de uso por plano** — cada organização tem um plano (`free`, `pro`) com limite mensal de uso de uma feature, calculado por período corrente e bloqueando a ação ao atingir o limite
- **API Keys** — emissão de chaves (`sk_live_...`) para autenticação de integrações externas:
  - a chave completa só é exibida uma única vez, no momento da criação
  - apenas o hash (SHA-256) é persistido — a chave nunca pode ser recuperada, somente revogada
  - listagem mostra só o prefixo mascarado, nunca a chave completa
  - revogação idempotente (chamar revoke em uma chave já revogada não gera erro)
- Auditoria básica registrando eventos como:
  - criação de organizações
  - criação de convites
  - aceite de convites
  - emissão e revogação de API Keys
- Schema do banco gerenciado inteiramente pelo **Alembic** — o servidor não recria mais as tabelas automaticamente no boot (uma decisão de segurança: evita perda acidental de dados a cada restart)
- **Integração contínua (CI)** — workflow do GitHub Actions que roda a suíte de testes automaticamente a cada `push` e `pull request` na branch `main`, aplicando as migrations via Alembic antes dos testes
- **Deploy em produção** — API no Render, PostgreSQL gerenciado pelo Supabase, com pool de conexões configurado para ambiente serverless (`NullPool`)

---

## Evidência verificada

A suíte de testes do backend foi executada com sucesso:

```bash
pytest -q
```

**Resultado:** ✅ 9 testes passaram

Os testes validam os principais fluxos implementados, incluindo:
- isolamento de dados entre organizações
- regras de autorização por role
- criação e aceitação de convites
- bloqueio de uso ao atingir a cota mensal

A cada `push` ou `pull request` para `main`, esses mesmos testes rodam automaticamente via GitHub Actions — o badge no topo deste README reflete o status em tempo real.

---

## Stack utilizada

**Backend**
- Python
- FastAPI
- SQLAlchemy 2.0 (Async)
- JWT (`python-jose`)
- Pytest
- Alembic (migrations — única fonte de verdade do schema)
- PostgreSQL (produção, via Supabase) / SQLite (desenvolvimento local)

**Frontend**
- React
- Vite
- Sistema de design próprio (CSS puro, sem framework de UI): paleta neutra fria com um único accent de sinalização, tipografia Space Grotesk + IBM Plex Mono

**Infraestrutura**
- Render (hospedagem da API)
- Supabase (PostgreSQL gerenciado)
- GitHub Actions (CI — testes automatizados a cada push/PR)

---

## Estrutura do projeto