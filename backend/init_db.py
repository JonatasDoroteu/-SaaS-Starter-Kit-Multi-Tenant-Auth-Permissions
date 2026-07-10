import asyncio

from app.db import engine
from app.models.base import Base
from app.models import membership, organization, user  # noqa: F401


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("tables-created")


if __name__ == "__main__":
    asyncio.run(main())
