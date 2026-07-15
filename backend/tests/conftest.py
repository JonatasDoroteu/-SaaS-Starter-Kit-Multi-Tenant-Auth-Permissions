from __future__ import annotations

import os

# Precisa rodar ANTES de qualquer import de app.*, porque app/db.py monta o
# engine do SQLAlchemy usando essa URL no momento do import. Assim, os
# testes usam um banco totalmente separado do saas_starter.db que você usa
# pra testar manualmente -- um nunca interfere no outro.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

import asyncio
from pathlib import Path

import pytest

from app.db import engine
from app.models.base import Base
from app.services.state import reset_store

TEST_DB_PATH = Path(__file__).parent.parent / "test.db"


@pytest.fixture(scope="session", autouse=True)
def _test_database():
    """Cria o schema do zero no banco de teste descartável, uma vez por
    sessão de testes, e apaga tudo no final -- isolado do banco que você
    usa manualmente."""

    async def _create_schema() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _drop_schema() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    asyncio.run(_create_schema())
    yield
    asyncio.run(_drop_schema())
    TEST_DB_PATH.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def clear_state() -> None:
    """Roda antes de cada teste: limpa os dados de todas as tabelas (não só
    o singleton Python do store) -- substitui o antigo comportamento de
    drop_all/create_all que fornecia esse isolamento como efeito colateral."""

    async def _truncate_all() -> None:
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())

    asyncio.run(_truncate_all())
    reset_store()