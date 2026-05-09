from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, debate, health, market, verdict
from app.core.config import settings
from app.services.user_store import user_store


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-powered multi-model stock and options debate engine.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix=settings.api_v1_prefix)
    app.include_router(auth.router, prefix=settings.api_v1_prefix)
    app.include_router(market.router, prefix=settings.api_v1_prefix)
    app.include_router(debate.router, prefix=settings.api_v1_prefix)
    app.include_router(verdict.router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    def startup() -> None:
        user_store.initialize()

    return app


app = create_app()
