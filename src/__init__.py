from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database.main import init_db
from src.users.routers import user_router
from src.auth.routers import auth_router


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


app.include_router(user_router)
app.include_router(auth_router)
