import os
import tempfile
import subprocess
from dataclasses import dataclass
from typing import Optional

from yt_dlp import YoutubeDL
import whisper


@dataclass
class VideoAnalysisResult:
    transcript: str
    duration_seconds: Optional[int]


_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        # можно взять "base" или "small" для ускорения
        _whisper_model = whisper.load_model("small")
    return _whisper_model


def _download_video(url: str) -> str:
    """
    Скачиваем видео по ссылке (vkvideo, vk.com, instagram)
    Возвращаем путь к mp4-файлу.
    """
    tmpdir = tempfile.mkdtemp(prefix="kupikod_video_")
    outtmpl = os.path.join(tmpdir, "video.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "mp4/best",
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        ext = info.get("ext", "mp4")

    video_path = os.path.join(tmpdir, f"video.{ext}")
    if not os.path.exists(video_path):
        # fallback: вдруг расширение другое
        for f in os.listdir(tmpdir):
            if f.startswith("video."):
                video_path = os.path.join(tmpdir, f)
                break

    return video_path


def _extract_audio(video_path: str) -> str:
    """
    Достаём аудио в wav 16kHz mono.
    """
    audio_path = os.path.join(os.path.dirname(video_path), "audio.wav")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        audio_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path


def _transcribe_audio(audio_path: str) -> VideoAnalysisResult:
    model = _get_whisper_model()
    result = model.transcribe(audio_path, language="ru")

    text = (result.get("text") or "").strip()

    duration_seconds: Optional[int] = None
    segments = result.get("segments") or []
    if segments:
        duration_seconds = int(segments[-1].get("end") or 0)

    return VideoAnalysisResult(
        transcript=text,
        duration_seconds=duration_seconds,
    )


def analyze_video_from_url(url: str) -> VideoAnalysisResult:
    """
    Полный цикл: скачать видео, вытащить аудио, сделать транскрипт.
    """
    video_path = _download_video(url)
    audio_path = _extract_audio(video_path)
    analysis = _transcribe_audio(audio_path)
    return analysis
