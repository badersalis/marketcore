import io
import logging
from dataclasses import dataclass
from typing import Tuple

from PIL import Image

logger = logging.getLogger(__name__)

_MAX_DIMENSION = 2048
_THUMB_SIZE = (400, 400)
_WEBP_QUALITY = 85


@dataclass(frozen=True)
class ProcessedImage:
    full: bytes    # resized + WebP encoded
    thumb: bytes   # 400×400 max, WebP encoded
    original_size: Tuple[int, int]
    final_size: Tuple[int, int]


class ImageProcessor:
    """Resize, optimise, and encode images to WebP.

    Input: raw bytes from any format PIL supports (JPEG, PNG, GIF first frame, etc.)
    Output: ProcessedImage with full-size and thumbnail variants as WebP bytes.
    """

    def process(self, raw: bytes) -> ProcessedImage:
        with Image.open(io.BytesIO(raw)) as img:
            original_size = img.size
            img = img.convert("RGB")

            if img.width > _MAX_DIMENSION or img.height > _MAX_DIMENSION:
                img.thumbnail((_MAX_DIMENSION, _MAX_DIMENSION), Image.LANCZOS)

            final_size = img.size
            full_buf = io.BytesIO()
            img.save(full_buf, "WEBP", quality=_WEBP_QUALITY, method=4)

            thumb = img.copy()
            thumb.thumbnail(_THUMB_SIZE, Image.LANCZOS)
            thumb_buf = io.BytesIO()
            thumb.save(thumb_buf, "WEBP", quality=80, method=4)

        logger.debug(
            "Processed image: %s → %s, full=%d bytes, thumb=%d bytes",
            original_size, final_size, len(full_buf.getvalue()), len(thumb_buf.getvalue()),
        )
        return ProcessedImage(
            full=full_buf.getvalue(),
            thumb=thumb_buf.getvalue(),
            original_size=original_size,
            final_size=final_size,
        )


__all__ = ["ImageProcessor", "ProcessedImage"]
