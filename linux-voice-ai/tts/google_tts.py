"""Text-to-Speech engine using Google TTS (gTTS)."""

import logging
from pathlib import Path
import tempfile
from gtts import gTTS

logger = logging.getLogger(__name__)


class GoogleTTS:
    """Google Text-to-Speech engine (simple and reliable)."""
    
    def __init__(self, lang='en', tld='com'):
        """
        Initialize Google TTS engine.
        
        Args:
            lang: Language code (default: 'en')
            tld: Top-level domain for accent (default: 'com' for US English)
        """
        self.lang = lang
        self.tld = tld
        self.temp_dir = Path(tempfile.gettempdir())
        
        logger.info(f"Initialized Google TTS: {lang} ({tld})")
    
    def synthesize(self, text, output_file=None):
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            output_file: Optional output file path
            
        Returns:
            Path: Path to generated audio file
        """
        if not text:
            logger.warning("Empty text provided for TTS")
            return None
        
        # Create output file if not provided
        if output_file is None:
            output_file = self.temp_dir / f"tts_output_{hash(text)}.mp3"
        
        output_file = Path(output_file)
        
        try:
            logger.info(f"Synthesizing: '{text}'")
            
            # Generate speech
            tts = gTTS(text=text, lang=self.lang, tld=self.tld, slow=False)
            tts.save(str(output_file))
            
            if output_file.exists():
                logger.info(f"TTS output saved: {output_file}")
                return output_file
            else:
                logger.error("TTS output file not created")
                return None
                
        except Exception as e:
            logger.error(f"Error during TTS synthesis: {e}")
            return None
    
    def speak(self, text):
        """
        Synthesize and return audio file path.
        
        Args:
            text: Text to speak
            
        Returns:
            Path: Path to audio file, or None if failed
        """
        return self.synthesize(text)
