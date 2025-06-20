from fastapi import Request
from starlette_context import context


def build_link_from_base_url(path: str) -> str:
    request: Request = context.get("base_url")
    return f"{request.base_url}{path}"
