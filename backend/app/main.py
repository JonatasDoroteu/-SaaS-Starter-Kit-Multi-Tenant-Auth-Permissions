from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, auth, invites, organizations, usage, api_keys
from app.services.state import seed_demo_user

app = FastAPI(title="SaaS Starter", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["organizations"])
app.include_router(invites.router, prefix="/api/v1/invites", tags=["invites"])
app.include_router(usage.router, prefix="/api/v1/usage", tags=["usage"])
app.include_router(api_keys.router, prefix="/api/v1/api-keys", tags=["api-keys"])


@app.on_event("startup")
async def startup_event() -> None:
    await seed_demo_user()