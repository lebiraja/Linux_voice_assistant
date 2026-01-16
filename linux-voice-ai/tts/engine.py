"""
Unified TTS Engine with fallback support.
Provides reliable text-to-speech with multiple backends.
"""

import logging
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TTSBackend(ABC):
    """Abstract base class for TTS backends"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend name"""
        pass

    @property
    @abstractmethod
    def requires_internet(self) -> bool:
        """Whether this backend needs internet"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available"""
        pass

    @abstractmethod
    def synthesize(self, text: str, output_path: Path) -> bool:
        """
        Synthesize speech to file.
        Returns True if successful.
        """
        pass


class GoogleTTSBackend(TTSBackend):
    """Google TTS backend (requires internet)"""

    def __init__(self, lang: str = 'en', tld: str = 'com'):
        self.lang = lang
        self.tld = tld
        self._gtts_available = None

    @property
    def name(self) -> str:
        return "Google TTS"

    @property
    def requires_internet(self) -> bool:
        return True

    def is_available(self) -> bool:
        if self._gtts_available is None:
            try:
                from gtts import gTTS
                self._gtts_available = True
            except ImportError:
                self._gtts_available = False
                logger.warning("gTTS not installed: pip install gtts")
        return self._gtts_available

    def synthesize(self, text: str, output_path: Path) -> bool:
        try:
            from gtts import gTTS

            tts = gTTS(text=text, lang=self.lang, tld=self.tld, slow=False)
            tts.save(str(output_path))

            if output_path.exists() and output_path.stat().st_size > 0:
                logger.debug(f"Google TTS synthesized: {output_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"Google TTS failed: {e}")
            return False


class PiperTTSBackend(TTSBackend):
    """Piper TTS backend (local, offline)"""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self._piper_binary = None

    @property
    def name(self) -> str:
        return "Piper TTS"

    @property
    def requires_internet(self) -> bool:
        return False

    def is_available(self) -> bool:
        # Check for piper binary
        self._piper_binary = shutil.which('piper')
        if self._piper_binary:
            # Check for model if specified
            if self.model_path:
                model = Path(self.model_path)
                if not model.exists():
                    logger.warning(f"Piper model not found: {self.model_path}")
                    return False
            return True
        return False

    def synthesize(self, text: str, output_path: Path) -> bool:
        try:
            # Build piper command
            cmd = [self._piper_binary, '--output_file', str(output_path)]

            if self.model_path:
                cmd.extend(['--model', self.model_path])

            # Run piper with text input
            process = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                capture_output=True,
                timeout=30
            )

            if process.returncode == 0 and output_path.exists():
                logger.debug(f"Piper TTS synthesized: {output_path}")
                return True

            logger.error(f"Piper failed: {process.stderr.decode()}")
            return False

        except subprocess.TimeoutExpired:
            logger.error("Piper TTS timed out")
            return False
        except Exception as e:
            logger.error(f"Piper TTS failed: {e}")
            return False


class EspeakTTSBackend(TTSBackend):
    """Espeak TTS backend (basic, always available on most Linux)"""

    def __init__(self, voice: str = 'en'):
        self.voice = voice
        self._espeak_binary = None

    @property
    def name(self) -> str:
        return "eSpeak TTS"

    @property
    def requires_internet(self) -> bool:
        return False

    def is_available(self) -> bool:
        self._espeak_binary = shutil.which('espeak') or shutil.which('espeak-ng')
        return self._espeak_binary is not None

    def synthesize(self, text: str, output_path: Path) -> bool:
        try:
            # espeak outputs WAV by default
            wav_path = output_path.with_suffix('.wav')

            cmd = [
                self._espeak_binary,
                '-v', self.voice,
                '-w', str(wav_path),
                text
            ]

            process = subprocess.run(cmd, capture_output=True, timeout=30)

            if process.returncode == 0 and wav_path.exists():
                # Rename to expected output path if different
                if wav_path != output_path:
                    wav_path.rename(output_path)
                logger.debug(f"eSpeak synthesized: {output_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"eSpeak failed: {e}")
            return False


class SpdSayTTSBackend(TTSBackend):
    """Speech-dispatcher TTS backend (uses system TTS, commonly available)"""

    def __init__(self):
        self._spd_say_binary = None

    @property
    def name(self) -> str:
        return "spd-say TTS"

    @property
    def requires_internet(self) -> bool:
        return False

    def is_available(self) -> bool:
        self._spd_say_binary = shutil.which('spd-say')
        return self._spd_say_binary is not None

    def synthesize(self, text: str, output_path: Path) -> bool:
        """
        spd-say doesn't output to file, so we use it as a direct speaker.
        For file output, we'll use espeak-ng library if available.
        """
        try:
            # Try to use espeak-ng library to write file
            espeak_ng = shutil.which('espeak-ng')
            if espeak_ng:
                wav_path = output_path.with_suffix('.wav')
                cmd = [espeak_ng, '-v', 'en', '-w', str(wav_path), text]
                process = subprocess.run(cmd, capture_output=True, timeout=30)
                if process.returncode == 0 and wav_path.exists():
                    logger.debug(f"espeak-ng synthesized: {wav_path}")
                    return True

            # Fallback: use festival if available
            festival = shutil.which('text2wave')
            if festival:
                wav_path = output_path.with_suffix('.wav')
                process = subprocess.run(
                    ['text2wave', '-o', str(wav_path)],
                    input=text.encode('utf-8'),
                    capture_output=True,
                    timeout=30
                )
                if process.returncode == 0 and wav_path.exists():
                    logger.debug(f"Festival synthesized: {wav_path}")
                    return True

            return False

        except Exception as e:
            logger.error(f"spd-say/espeak-ng failed: {e}")
            return False

    def speak_directly(self, text: str) -> bool:
        """Speak directly through speakers (no file)"""
        try:
            # Use spd-say for direct speech
            process = subprocess.run(
                [self._spd_say_binary, '-w', text],  # -w waits until done
                capture_output=True,
                timeout=60
            )
            return process.returncode == 0
        except Exception as e:
            logger.error(f"spd-say direct speech failed: {e}")
            return False


class UnifiedTTSEngine:
    """
    Unified TTS engine with automatic fallback.

    Priority order:
    1. Piper (local, high quality) - if available
    2. Google TTS (requires internet, high quality)
    3. eSpeak (basic, always available)
    """

    def __init__(self, config: dict = None):
        config = config or {}

        self.temp_dir = Path(tempfile.gettempdir()) / 'jarvis_tts'
        self.temp_dir.mkdir(exist_ok=True)

        # Initialize backends
        self.backends: list[TTSBackend] = []

        # Google TTS (high quality, needs internet)
        google_config = config.get('google', {})
        self.backends.append(GoogleTTSBackend(
            lang=google_config.get('lang', 'en'),
            tld=google_config.get('tld', 'com')
        ))

        # Piper TTS (local, high quality)
        piper_config = config.get('piper', {})
        self.backends.append(PiperTTSBackend(
            model_path=piper_config.get('model_path')
        ))

        # spd-say / espeak-ng (commonly available on Linux)
        self.backends.append(SpdSayTTSBackend())

        # eSpeak (basic fallback)
        espeak_config = config.get('espeak', {})
        self.backends.append(EspeakTTSBackend(
            voice=espeak_config.get('voice', 'en')
        ))

        # Filter to available backends
        self.available_backends = [b for b in self.backends if b.is_available()]

        if self.available_backends:
            logger.info(f"TTS backends available: {[b.name for b in self.available_backends]}")
        else:
            logger.error("No TTS backends available!")

        # Track which backend works
        self.last_working_backend: Optional[TTSBackend] = None

    def speak(self, text: str) -> Optional[Path]:
        """
        Synthesize speech from text.

        Args:
            text: Text to speak

        Returns:
            Path to audio file, or None if all backends fail
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return None

        # Generate unique filename
        text_hash = hash(text) & 0xFFFFFFFF  # Positive hash
        output_path = self.temp_dir / f"tts_{text_hash}.mp3"

        # Try cached file first
        if output_path.exists() and output_path.stat().st_size > 0:
            logger.debug(f"Using cached TTS: {output_path}")
            return output_path

        # Try last working backend first
        if self.last_working_backend:
            if self._try_backend(self.last_working_backend, text, output_path):
                return output_path

        # Try all backends in order
        for backend in self.available_backends:
            if backend == self.last_working_backend:
                continue  # Already tried

            if self._try_backend(backend, text, output_path):
                self.last_working_backend = backend
                return output_path

        logger.error("All TTS backends failed!")
        return None

    def _try_backend(self, backend: TTSBackend, text: str, output_path: Path) -> bool:
        """Try to synthesize with a specific backend"""
        try:
            logger.debug(f"Trying {backend.name}...")

            # Determine file extension based on backend
            if isinstance(backend, GoogleTTSBackend):
                actual_path = output_path.with_suffix('.mp3')
            else:
                actual_path = output_path.with_suffix('.wav')

            if backend.synthesize(text, actual_path):
                # Ensure file exists and has content
                if actual_path.exists() and actual_path.stat().st_size > 0:
                    # Rename to expected path if different
                    if actual_path != output_path:
                        # Keep original extension or convert later
                        pass
                    logger.info(f"TTS success with {backend.name}")
                    return True

            return False

        except Exception as e:
            logger.error(f"{backend.name} failed: {e}")
            return False

    def synthesize(self, text: str, output_file: Optional[str] = None) -> Optional[Path]:
        """
        Synthesize speech to a specific file.
        Alias for speak() with custom output path.
        """
        if output_file:
            result = self.speak(text)
            if result:
                # Copy to specified location
                target = Path(output_file)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(result, target)
                return target
            return None
        return self.speak(text)

    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove old TTS cache files"""
        import time
        now = time.time()
        max_age_seconds = max_age_hours * 3600

        for file in self.temp_dir.glob("tts_*"):
            try:
                if now - file.stat().st_mtime > max_age_seconds:
                    file.unlink()
                    logger.debug(f"Cleaned up old TTS file: {file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {file}: {e}")

    def get_status(self) -> dict:
        """Get TTS engine status"""
        return {
            "available_backends": [b.name for b in self.available_backends],
            "last_working": self.last_working_backend.name if self.last_working_backend else None,
            "cache_dir": str(self.temp_dir),
            "cached_files": len(list(self.temp_dir.glob("tts_*")))
        }


# Convenience function to create engine with default config
def create_tts_engine(config: dict = None) -> UnifiedTTSEngine:
    """Create a TTS engine with the given config"""
    return UnifiedTTSEngine(config)
