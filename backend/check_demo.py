import asyncio
from app.services.state import store

async def main() -> None:
    await store._ensure_initialized()
    print('before', await store.get_user('demo@example.com'))
    print('seed', await store.seed_demo_user())
    print('after', await store.get_user('demo@example.com'))

asyncio.run(main())
