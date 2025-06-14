from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routers import auth_router
from src.db.main import init_db
from src.users.routers import user_router
from src.utils.exceptions import register_exceptions
from src.utils.middlewares import register_middlewares


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server started...")
    await init_db()
    yield
    print("Server stopped...")


version = "v1"

app = FastAPI(
    title="FastAPI Template",
    description="A template for my FASTAPI apps to make things very easy for me whenever I am starting a new project.",
    version=version,
    lifespan=life_span,
)

register_exceptions(app)
register_middlewares(app)

app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(user_router, prefix=f"/api/{version}/users", tags=["user"])
