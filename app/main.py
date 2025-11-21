from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ← добавили
import subprocess
import whisper

from .database import Base, engine
from .routers import bloggers, integrations

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kupikod integrations tracker",
    version="0.2.0",
)

# 👇 вот этот блок добавь сразу после создания app
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bloggers.router)
app.include_router(integrations.router)

@app.get("/debug/env")
def debug_env():
    try:
        ffmpeg_ok = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        ).returncode == 0
    except Exception:
        ffmpeg_ok = False

    try:
        model = whisper.load_model("small")
        whisper_ok = model is not None
    except Exception:
        whisper_ok = False

    return {"ffmpeg": ffmpeg_ok, "whisper": whisper_ok}


@app.get("/")
def root():
    return {"status": "ok", "message": "Kupikod tracker API"}
