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
    title="SRH Expense Tracker",
    description="A REST API for SRH Expense tracker",
    version=version,
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/mit"},
    contact={"name": "Theo Flux", "email": "tifluse@gmail.com", "url": "https://github.com/Theo-flux/fast-template"},
    docs_url=f"/api/{version}/docs",
    openapi_url=f"/api/{version}/openapi.json",
    lifespan=life_span,
)

register_exceptions(app)
register_middlewares(app)


app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(user_router, prefix=f"/api/{version}/users", tags=["user"])
