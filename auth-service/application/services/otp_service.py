import secrets

from redis.asyncio import Redis


class OtpService:
    _PREFIX = "email_verification:"

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def generate(self) -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    async def store(self, user_id: str, otp: str, expire_minutes: int) -> None:
        await self._redis.set(
            f"{self._PREFIX}{user_id}", otp, ex=expire_minutes * 60
        )

    async def verify_and_consume(self, user_id: str, otp: str) -> bool:
        """Validates the OTP and deletes it — single-use guarantee."""
        key = f"{self._PREFIX}{user_id}"
        stored = await self._redis.get(key)
        if not stored or stored != otp:
            return False
        await self._redis.delete(key)
        return True


__all__ = ["OtpService"]
