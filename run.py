"""
Entrypoint script for running the application.
Reads PORT from environment variable.
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting application on port {port}...")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
