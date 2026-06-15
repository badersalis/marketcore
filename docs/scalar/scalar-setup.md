# Scalar API Reference — Setup Guide

Each service serves its own interactive API documentation at `/docs` using [Scalar](https://scalar.com), a modern alternative to Swagger UI.

## How It Works

Scalar is loaded via CDN — no additional Python package is required. Each service's `main.py` registers a `/docs` endpoint that returns a minimal HTML page pointing Scalar at `/openapi.json` (FastAPI's built-in OpenAPI schema endpoint).

```python
from fastapi.responses import HTMLResponse

@app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
async def scalar_docs():
    return HTMLResponse(content="""
<!doctype html>
<html>
  <head>
    <title>My Service — API Reference</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body>
    <script
      id="api-reference"
      data-url="/openapi.json"
      data-configuration='{"theme":"purple","layout":"modern"}'
    ></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </body>
</html>
""")
```

The default Swagger UI and ReDoc are disabled:
```python
app = FastAPI(..., docs_url=None, redoc_url=None)
```

## Service Endpoints

| Service | Scalar Docs URL |
|---|---|
| auth-service | http://localhost:8001/docs |
| product-service | http://localhost:8002/docs |
| payment-service | http://localhost:8004/docs |

## Configuration Options

Pass a JSON object to `data-configuration` on the `<script>` tag:

```json
{
  "theme": "purple",
  "layout": "modern",
  "defaultHttpClient": {
    "targetKey": "python",
    "clientKey": "requests"
  },
  "hideDownloadButton": false,
  "searchHotKey": "k"
}
```

Available themes: `purple`, `default`, `alternate`, `moon`, `solarized`, `bluePlanet`, `saturn`, `kepler`, `mars`.

## File Upload Documentation

For endpoints that accept file uploads (e.g., product images), FastAPI documents them correctly when you use `UploadFile` and `File`:

```python
from fastapi import File, UploadFile

@router.post("/products/{id}/image")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(..., description="Product image (JPEG/PNG, max 5 MB)"),
):
    ...
```

Scalar renders these as proper file-upload fields in the interactive UI — no extra configuration needed. The generated OpenAPI schema uses `multipart/form-data` with `format: binary`.

**Multiple files:**
```python
from typing import Annotated
from fastapi import File, UploadFile

@router.post("/products/{id}/images")
async def upload_product_images(
    files: Annotated[list[UploadFile], File(description="Up to 10 product images")],
):
    ...
```

## Grouping Endpoints by Service

Each service tags its routes when calling `include_router`:

```python
app.include_router(payment_router, prefix="/payments", tags=["Payments"])
```

Scalar groups operations by tag in the sidebar, providing clean per-service navigation.

## Pinning the Scalar Version

The CDN URL `https://cdn.jsdelivr.net/npm/@scalar/api-reference` always resolves to the latest version. For production stability, pin a specific version:

```html
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.25.0"></script>
```

Check the [Scalar releases page](https://github.com/scalar/scalar/releases) for the current stable version.

## Offline / Air-Gapped Environments

Download the bundle and serve it as a static file:

```bash
npm pack @scalar/api-reference
# or
curl -o scalar.js https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.25.0
```

Mount it in FastAPI:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
# Then reference /static/scalar.js in the HTML
```
