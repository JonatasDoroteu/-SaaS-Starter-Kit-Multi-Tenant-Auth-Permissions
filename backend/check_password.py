import asyncio
from app.core.security import verify_password
from app.services.state import store

async def main() -> None:
    await store._ensure_initialized()
    user = await store.get_user('demo@example.com')
    print(user)
    print(verify_password('secret123', user['password_hash']))

asyncio.run(main())
