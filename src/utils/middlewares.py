from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette_context import context, plugins
from starlette_context.middleware import RawContextMiddleware


async def custom_context_middleware(request, call_next):
    context["base_url"] = str(request.base_url)
    return await call_next(request)


def register_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    app.add_middleware(BaseHTTPMiddleware, dispatch=custom_context_middleware)

    app.add_middleware(
        RawContextMiddleware,
        plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin(),
            plugins.UserAgentPlugin(),
        ),
    )
