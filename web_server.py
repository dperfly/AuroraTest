"""AuroraTest Web Server entrypoint."""
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api import router as api_router

app = FastAPI(title="AuroraTest API")
app.include_router(api_router)


@app.get("/")
async def root():
    return FileResponse("web/index.html")


if os.path.exists("web"):
    app.mount("/web", StaticFiles(directory="web", html=True), name="web")


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("AuroraTest Web Server")
    print("访问地址: http://localhost:8002")
    print("默认账号: admin / admin123")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8002)
