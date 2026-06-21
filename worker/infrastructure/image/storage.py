import abc
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageClient(abc.ABC):
    @abc.abstractmethod
    async def upload(self, data: bytes, filename: str) -> str:
        """Upload processed image bytes and return the public URL."""
        ...


class LocalStorageClient(StorageClient):
    """Dev stub — saves files to disk and returns a file:// URL.

    Swap this for an S3Client or CloudinaryClient in production:
        async def upload(self, data, filename):
            s3.put_object(Bucket=self._bucket, Key=filename, Body=data, ContentType="image/webp")
            return f"https://{self._bucket}.s3.amazonaws.com/{filename}"
    """

    def __init__(self, base_dir: str = "/tmp/marketcore-images") -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, data: bytes, filename: str) -> str:
        dest = self._base_dir / filename
        dest.write_bytes(data)
        logger.debug("LocalStorage: saved %s (%d bytes)", dest, len(data))
        return f"file://{dest}"


__all__ = ["StorageClient", "LocalStorageClient"]
