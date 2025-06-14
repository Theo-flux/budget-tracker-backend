import aioredis

from src.config import Config

token_block_list = aioredis.StrictRedis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db="token_block_list_db"
)

JTI_EXPIRY = 3600


async def add_jti_to_block_list(jti: str) -> None:
    return await token_block_list.set(name=jti, value="", ex=JTI_EXPIRY)


async def token_in_block_list(jti: str) -> bool:
    blocked_jti = await token_block_list.get(jti)

    return blocked_jti is not None
