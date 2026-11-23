import uvicorn

from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        # Dev only: also restart when the roadmap data changes (it's cached in memory).
        reload_includes=["*.py", "app/data/*.json"],
    )
