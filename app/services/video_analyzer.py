import os
import tempfile
import subprocess
from dataclasses import dataclass
from typing import Optional

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import whisper


@dataclass
class VideoAnalysisResult:
    transcript: str
    duration_seconds: Optional[int]


class VideoAnalysisError(Exception):
    pass


_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        # можешь взять "base" или "small"
        _whisper_model = whisper.load_model("small")
    return _whisper_model


def _download_video(url: str) -> str:
    tmpdir = tempfile.mkdtemp(prefix="kupikod_video_")
    outtmpl = os.path.join(tmpdir, "video.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "mp4/best",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get("ext", "mp4")
    except DownloadError as e:
        raise VideoAnalysisError(f"Не удалось скачать видео: {e}") from e
    except Exception as e:
        raise VideoAnalysisError(f"Ошибка при скачивании видео: {e!r}") from e

    video_path = os.path.join(tmpdir, f"video.{ext}")
    if not os.path.exists(video_path):
        # fallback - ищем любой video.*
        for f in os.listdir(tmpdir):
            if f.startswith("video."):
                video_path = os.path.join(tmpdir, f)
                break

    if not os.path.exists(video_path):
        raise VideoAnalysisError("Не удалось найти скачанный видеофайл")

    return video_path


def _extract_audio(video_path: str) -> str:
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
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        raise VideoAnalysisError(f"Ошибка при извлечении аудио через ffmpeg: {e}") from e

    if not os.path.exists(audio_path):
        raise VideoAnalysisError("Не удалось создать аудиофайл для транскрибации")

    return audio_path


def _transcribe_audio(audio_path: str) -> VideoAnalysisResult:
    try:
        model = _get_whisper_model()
    except Exception as e:
        raise VideoAnalysisError(f"Не удалось загрузить модель Whisper: {e!r}") from e

    try:
        result = model.transcribe(audio_path, language="ru")
    except Exception as e:
        raise VideoAnalysisError(f"Ошибка при транскрибации аудио: {e!r}") from e

    text = (result.get("text") or "").strip()
    duration_seconds: Optional[int] = None
    segments = result.get("segments") or []
    if segments:
        duration_seconds = int(segments[-1].get("end") or 0)

    if not text:
        raise VideoAnalysisError("Транскрипт получился пустым")

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
