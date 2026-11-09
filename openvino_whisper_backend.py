"""
Optional OpenVINO GenAI Whisper backend for Intel GPUs (Arc / iGPU).

Imports of openvino / openvino_genai are deferred until
`try_create_openvino_whisper()` is called, so machines without Intel GPUs never
pay the import cost when the caller probes hardware first.
"""

from __future__ import annotations

import os
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np

# Official OpenVINO IR exports on Hugging Face (int8 = good default size/speed).
OV_MODEL_IDS = {
    "tiny": "OpenVINO/whisper-tiny-int8-ov",
    "base": "OpenVINO/whisper-base-int8-ov",
    "small": "OpenVINO/whisper-small-int8-ov",
    "medium": "OpenVINO/whisper-medium-int8-ov",
    # UI/CLI "large" maps to multilingual large-v3 IR.
    "large": "OpenVINO/whisper-large-v3-int8-ov",
}


@dataclass
class TranscriptWord:
    """Duck-types faster-whisper word objects (`.word`, `.start`, `.end`)."""

    word: str
    start: float
    end: float


class OpenVINOWhisperTranscriber:
    """Thin wrapper around OpenVINO GenAI Whisper/ASR pipeline."""

    def __init__(self, pipeline, model_id: str, ov_device: str, model_dir: Path):
        self.pipeline = pipeline
        self.model_id = model_id
        self.ov_device = ov_device
        self.model_dir = model_dir

    def transcribe_words(self, audio_path: Path) -> Tuple[List[TranscriptWord], float]:
        audio = _load_wav_mono_16k(audio_path)
        duration = float(len(audio) / 16000.0)

        # word_timestamps must be enabled on the pipeline (constructor) and generate().
        generate_kwargs = {
            "language": "<|en|>",
            "task": "transcribe",
            "return_timestamps": True,
            "word_timestamps": True,
        }
        try:
            result = self.pipeline.generate(audio.tolist(), **generate_kwargs)
        except TypeError:
            # Older genai builds may only accept a config object / fewer kwargs.
            result = self.pipeline.generate(audio.tolist())

        words = _extract_words(result)
        return words, duration


def openvino_packages_importable() -> bool:
    """True if the optional Intel extras are installed (still a lazy import)."""
    try:
        import openvino  # noqa: F401
        import openvino_genai  # noqa: F401
        return True
    except Exception:
        return False


def openvino_gpu_device_name() -> Optional[str]:
    """
    Return an OpenVINO GPU device string if the runtime sees one.

    Imports OpenVINO. Call only after an Intel hardware hint (or forced mode).
    """
    try:
        import openvino as ov
    except Exception:
        return None
    try:
        core = ov.Core()
        available = list(core.available_devices)
    except Exception:
        return None
    for name in available:
        if str(name).upper().startswith("GPU"):
            return str(name)
    return None


def try_create_openvino_whisper(
    model_size: str,
    prefer_gpu: bool = True,
) -> Optional[OpenVINOWhisperTranscriber]:
    """
    Build an OpenVINO Whisper transcriber if packages + device are available.

    Returns None on any failure so callers can fall back to faster-whisper.
    """
    size = (model_size or "base").strip().lower()
    model_id = OV_MODEL_IDS.get(size)
    if model_id is None:
        print(f"  ⚠ OpenVINO has no mapped model for size '{model_size}'; skipping")
        return None

    try:
        import openvino_genai as ov_genai
        from huggingface_hub import snapshot_download
    except Exception as exc:
        print(
            "  ⚠ Intel GPU path needs optional packages "
            f"(openvino, openvino-genai, huggingface_hub): {exc}"
        )
        print("     Install with: python3 -m pip install -r requirements-intel.txt")
        return None

    ov_device = None
    if prefer_gpu:
        ov_device = openvino_gpu_device_name()
    if not ov_device:
        # Forced openvino with no GPU: still allow CPU OpenVINO if explicitly wanted,
        # but auto-detect path should not take this branch for "Intel GPU support".
        if prefer_gpu:
            print("  ⚠ OpenVINO imported but no GPU device is visible; skipping Intel path")
            return None
        ov_device = "CPU"

    model_dir = _model_cache_dir(model_id)
    print(f"  Loading OpenVINO Whisper model: {model_id} → {ov_device}")
    print(
        "  ⚠ Intel OpenVINO path is BETA — not yet validated on a real Arc card "
        "in this project; falling back to CPU if inference fails."
    )
    print(f"  Cache dir: {model_dir}")
    try:
        snapshot_download(repo_id=model_id, local_dir=str(model_dir))
    except Exception as exc:
        print(f"  ⚠ Failed to download OpenVINO model '{model_id}': {exc}")
        return None

    pipeline = _build_pipeline(ov_genai, model_dir, ov_device)
    if pipeline is None:
        return None

    print(f"  ✓ OpenVINO Whisper ready on {ov_device} ({model_id})")
    return OpenVINOWhisperTranscriber(
        pipeline=pipeline,
        model_id=model_id,
        ov_device=ov_device,
        model_dir=model_dir,
    )


def _build_pipeline(ov_genai, model_dir: Path, ov_device: str):
    """Create ASR/Whisper pipeline with word timestamps when the API allows it."""
    errors = []
    # Prefer ASRPipeline (newer GenAI); fall back to WhisperPipeline.
    pipeline_ctors = []
    if hasattr(ov_genai, "ASRPipeline"):
        pipeline_ctors.append(("ASRPipeline", ov_genai.ASRPipeline))
    if hasattr(ov_genai, "WhisperPipeline"):
        pipeline_ctors.append(("WhisperPipeline", ov_genai.WhisperPipeline))
    if not pipeline_ctors:
        print("  ⚠ openvino-genai has neither ASRPipeline nor WhisperPipeline")
        return None

    for name, ctor in pipeline_ctors:
        for kwargs in (
            {"word_timestamps": True},
            {},
        ):
            try:
                return ctor(str(model_dir), ov_device, **kwargs)
            except TypeError as exc:
                errors.append(f"{name}{kwargs}: {exc}")
                try:
                    return ctor(str(model_dir), ov_device)
                except Exception as exc2:
                    errors.append(f"{name}(): {exc2}")
            except Exception as exc:
                errors.append(f"{name}{kwargs}: {exc}")
                continue
    print("  ⚠ Could not construct OpenVINO Whisper pipeline:")
    for err in errors[:4]:
        print(f"     - {err}")
    return None


def _model_cache_dir(model_id: str) -> Path:
    hf_home = os.environ.get("HF_HOME") or os.environ.get("XDG_CACHE_HOME")
    if hf_home:
        root = Path(hf_home) / "profanity-filter-openvino"
    else:
        root = Path.home() / ".cache" / "profanity-filter-openvino"
    safe = model_id.replace("/", "__")
    path = root / safe
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_wav_mono_16k(audio_path: Path) -> np.ndarray:
    with wave.open(str(audio_path), "rb") as wf:
        channels = wf.getnchannels()
        rate = wf.getframerate()
        sampwidth = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())
    if sampwidth != 2:
        raise RuntimeError(f"Expected 16-bit WAV, got sampwidth={sampwidth}")
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    if rate != 16000:
        # Detector already extracts 16 kHz; keep a clear error if that changes.
        raise RuntimeError(f"Expected 16 kHz WAV for OpenVINO Whisper, got {rate} Hz")
    return audio


def _extract_words(result) -> List[TranscriptWord]:
    raw_groups = getattr(result, "words", None)
    items: Sequence = []
    if raw_groups is None:
        items = []
    elif len(raw_groups) == 0:
        items = []
    else:
        first = raw_groups[0]
        # GenAI may return List[WhisperWordTiming] or List[List[...]] per chunk.
        if hasattr(first, "start_ts") or hasattr(first, "start") or hasattr(first, "word") or hasattr(first, "text"):
            items = raw_groups
        else:
            # Flatten nested chunk lists.
            flat: List = []
            for group in raw_groups:
                try:
                    flat.extend(list(group))
                except TypeError:
                    flat.append(group)
            items = flat

    words: List[TranscriptWord] = []
    for item in items:
        text = (
            getattr(item, "word", None)
            or getattr(item, "text", None)
            or ""
        )
        text = str(text).strip()
        if not text:
            continue
        start = getattr(item, "start_ts", None)
        end = getattr(item, "end_ts", None)
        if start is None:
            start = getattr(item, "start", 0.0)
        if end is None:
            end = getattr(item, "end", start)
        words.append(
            TranscriptWord(
                word=text,
                start=float(start or 0.0),
                end=float(end or 0.0),
            )
        )
    return words
