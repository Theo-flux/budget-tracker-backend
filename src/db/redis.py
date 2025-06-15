import logging

import aioredis

from src.config import Config

token_block_list = None

try:
    token_block_list = aioredis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)
except ConnectionError:
    print("Redis not available. Skipping blocklist feature.")


async def add_jti_to_block_list(jti: str) -> None:
    return await token_block_list.set(name=jti, value="", ex=3600)


async def token_in_block_list(jti: str) -> bool:
    if await token_block_list is None:
        return False

    try:
        blocked_jti = await token_block_list.get(jti)
        return blocked_jti is not None
    except Exception as e:
        logging.warning(f"Redis error: {e}")
        return False
