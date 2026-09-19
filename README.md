
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
alembic upgrade head         # aplica o schema — obrigatório antes do primeiro start
uvicorn app.main:app --reload
```

O backend sobe em `http://127.0.0.1:8000`. Documentação interativa (Swagger) disponível em `http://127.0.0.1:8000/docs`.

Em modo de desenvolvimento (`DEBUG=true` no `.env`), um usuário de demonstração é criado automaticamente ao iniciar o servidor, para facilitar testes locais rápidos. Esse comportamento é desativado em produção.

**Variáveis de ambiente obrigatórias:** copie `.env.example` para `.env` e defina pelo menos `SECRET_KEY` (chave de assinatura dos tokens JWT) — a aplicação recusa subir sem ela. Gere um valor seguro com:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
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

### CI/CD

O projeto conta com um workflow de integração contínua (`.github/workflows/ci.yml`) que, a cada `push` ou `pull request` na branch `main`:

1. Faz checkout do código
2. Configura o Python 3.11 com cache de dependências
3. Instala as dependências do `backend/requirements.txt`
4. Aplica as migrations com `alembic upgrade head`
5. Roda a suíte de testes com `pytest -q`

O workflow define `SECRET_KEY` como variável de ambiente exclusiva para o CI, já que esse campo é obrigatório e não tem valor default — uma decisão intencional para evitar que a aplicação suba, em qualquer ambiente, com uma chave de assinatura JWT previsível.

---

## Próximos passos

- [x] Migração para PostgreSQL em produção
- [x] Deploy da API em produção (Render + Supabase)
- [x] Pipeline de CI/CD com GitHub Actions
- [ ] Row Level Security (RLS) nas tabelas do Supabase
- [ ] Expansão da cobertura de testes (incluindo o fluxo completo de API Keys)
- [ ] Deploy do frontend em produção
- [ ] Docker e Docker Compose completos
- [ ] Rate limiting por API Key
- [ ] Escopos/permissões granulares por chave (hoje uma chave tem acesso total à organização)
- [ ] Sistema de permissões mais granular, independente das roles
- [ ] Evolução do sistema de convites (reenvio, recusa, notificações por e-mail e histórico)
- [ ] Auditoria mais robusta e consultável

---

## Sobre o projeto

O projeto ainda está em desenvolvimento, mas já evoluiu para uma base próxima da arquitetura utilizada em aplicações SaaS reais, explorando conceitos como multi-tenancy, autenticação, autorização, cotas de uso por plano, emissão segura de credenciais e boas práticas de backend.

Três decisões técnicas que valeram a pena destacar:

- **Refresh token e API Keys não são JWT** — são valores aleatórios de alta entropia, persistidos apenas como hash. Isso permite revogação imediata (algo que um JWT sozinho não garante bem, já que é válido até expirar) e elimina o risco de um segredo em texto puro vazar do banco.
- **O schema do banco é gerenciado só pelo Alembic** — numa versão anterior, o próprio app recriava as tabelas a cada subida do servidor, um atalho conveniente em desenvolvimento solo mas destrutivo em qualquer ambiente real. Corrigido para que toda mudança de schema passe por uma migração versionada.
- **Pool de conexões assíncrono ajustado para ambiente serverless** — em produção, o engine usa `NullPool` em vez do pool padrão, evitando que conexões fiquem presas a um event loop que não existe mais entre requisições (um problema real de asyncio + SQLAlchemy async em plataformas como Render).

---

`#Python` `#FastAPI` `#React` `#Vite` `#SQLAlchemy` `#JWT` `#RBAC` `#SaaS` `#Backend` `#SoftwareEngineering` `#APIs` `#MultiTenant` `#Docker` `#PostgreSQL` `#GitHub` `#OpenSource` `#WebDevelopment`