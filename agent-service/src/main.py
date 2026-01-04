"""Main entry point for the agent service."""
import os

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV") == "development",
    )
