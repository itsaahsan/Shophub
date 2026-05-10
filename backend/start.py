"""Production entry point for hosts that provide a PORT environment variable."""

import os

import uvicorn


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
