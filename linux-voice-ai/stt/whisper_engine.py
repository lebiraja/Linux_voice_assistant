"""Speech-to-Text engine using Whisper."""

from faster_whisper import WhisperModel
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WhisperEngine:
    """Whisper-based speech-to-text engine."""
    
    def __init__(self, model_name="tiny", device="cpu", compute_type="int8", language="en"):
        """
        Initialize Whisper STT engine.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu, cuda)
            compute_type: Computation type (int8, float16, float32)
            language: Language code for transcription
        """
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.model = None
        
        logger.info(f"Initializing Whisper model: {model_name} on {device}")
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def transcribe(self, audio_file):
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            str: Transcribed text, or None if transcription failed
        """
        audio_file = Path(audio_file)
        
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_file}")
            return None
        
        try:
            logger.info(f"Transcribing: {audio_file}")
            
            # Transcribe
            segments, info = self.model.transcribe(
                str(audio_file),
                language=self.language,
                beam_size=5,
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(
                    min_silence_duration_ms=1000,
                    speech_pad_ms=400,
                    threshold=0.5
                )
            )
            
            # Combine all segments
            text = " ".join([segment.text for segment in segments]).strip()
            
            logger.info(f"Transcription: '{text}'")
            logger.debug(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            return text if text else None
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None
    
    def transcribe_with_timestamps(self, audio_file):
        """
        Transcribe audio file with word-level timestamps.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            list: List of segments with timestamps and text
        """
        audio_file = Path(audio_file)
        
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_file}")
            return None
        
        try:
            segments, info = self.model.transcribe(
                str(audio_file),
                language=self.language,
                word_timestamps=True
            )
            
            result = []
            for segment in segments:
                result.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error during transcription with timestamps: {e}")
            return None
