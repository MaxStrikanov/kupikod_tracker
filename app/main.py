from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess

from .database import Base, engine
from .routers import bloggers, integrations

# создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kupikod integrations tracker",
    version="0.2.0",
)

# ---- CORS, чтобы фронт мог ходить на API ----
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # на первое время можно вообще открыть
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Роуты ----
app.include_router(bloggers.router)
app.include_router(integrations.router)


@app.get("/debug/env")
def debug_env():
    """
    Небольшая проверка окружения:
    - виден ли ffmpeg
    """
    try:
        proc = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        ffmpeg_ok = proc.returncode == 0
    except Exception:
        ffmpeg_ok = False

    return {"ffmpeg": ffmpeg_ok}


@app.get("/")
def root():
    return {"status": "ok", "message": "Kupikod tracker API"}
