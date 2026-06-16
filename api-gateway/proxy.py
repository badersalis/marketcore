import logging
from typing import Optional

import httpx
from asgi_correlation_id import correlation_id as _correlation_id_ctx
from fastapi import Request, Response
from fastapi.responses import StreamingResponse

from core.config import UPSTREAM_MAP

logger = logging.getLogger(__name__)

# Headers to strip before forwarding (hop-by-hop)
_HOP_BY_HOP = {
    "connection", "keep-alive", "transfer-encoding", "te",
    "trailers", "upgrade", "proxy-authorization", "proxy-authenticate",
}


def _upstream_for(path: str) -> Optional[str]:
    for prefix, url in UPSTREAM_MAP.items():
        if path.startswith(prefix):
            return url
    return None


async def reverse_proxy(request: Request) -> Response:
    path = request.url.path
    query = request.url.query
    upstream = _upstream_for(path)

    if upstream is None:
        return Response(content='{"detail":"No upstream for this path"}', status_code=404, media_type="application/json")

    target_url = f"{upstream}{path}"
    if query:
        target_url += f"?{query}"

    # Build forwarding headers
    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP
    }
    corr_id = _correlation_id_ctx.get(None)
    if corr_id:
        forward_headers["X-Correlation-ID"] = corr_id

    body = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            upstream_response = await client.request(
                method=request.method,
                url=target_url,
                headers=forward_headers,
                content=body,
                follow_redirects=False,
            )
        except httpx.ConnectError:
            logger.error("Cannot connect to upstream %s", upstream)
            return Response(
                content='{"detail":"Upstream service unavailable"}',
                status_code=503,
                media_type="application/json",
            )
        except httpx.TimeoutException:
            logger.error("Upstream %s timed out", upstream)
            return Response(
                content='{"detail":"Upstream service timed out"}',
                status_code=504,
                media_type="application/json",
            )

    response_headers = {
        k: v for k, v in upstream_response.headers.items()
        if k.lower() not in _HOP_BY_HOP | {"content-length"}
    }
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )


__all__ = ["reverse_proxy"]
