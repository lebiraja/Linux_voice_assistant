"""Text-to-Speech engine using Piper."""

import subprocess
import logging
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class PiperTTS:
    """Piper-based text-to-speech engine."""
    
    def __init__(self, model_name="en_US-lessac-medium", speaker=0):
        """
        Initialize Piper TTS engine.
        
        Args:
            model_name: Piper voice model name
            speaker: Speaker ID for multi-speaker models
        """
        self.model_name = model_name
        self.speaker = speaker
        self.temp_dir = Path(tempfile.gettempdir())
        
        logger.info(f"Initialized Piper TTS: {model_name}")
    
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
            output_file = self.temp_dir / f"tts_output_{hash(text)}.wav"
        
        output_file = Path(output_file)
        
        try:
            logger.info(f"Synthesizing: '{text}'")
            
            # ALWAYS check absolute Docker path first (models baked into image)
            model_base = Path(f"/app/models/piper/{self.model_name}")
            model_file = model_base.with_suffix('.onnx')
            config_file = model_base.with_suffix('.onnx.json')
            
            # Only try relative path if absolute doesn't exist (for local development)
            if not model_file.exists():
                logger.debug(f"Docker model path not found, trying local path")
                model_base = Path(f"models/piper/{self.model_name}")
                model_file = model_base.with_suffix('.onnx')
                config_file = model_base.with_suffix('.onnx.json')
            
            if not model_file.exists():
                logger.error(f"Model file not found at: {model_file}")
                logger.error(f"Also checked: /app/models/piper/{self.model_name}.onnx")
                logger.error(f"Please ensure Piper model is downloaded")
                return None
            
            logger.info(f"Using model: {model_file}")
            
            # Use piper with explicit model and config files
            cmd = [
                'piper',
                '--model', str(model_file),
                '--config', str(config_file),
                '--output_file', str(output_file)
            ]
            
            logger.debug(f"Running Piper with model: {model_file}")
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                logger.error(f"Piper TTS error: {stderr}")
                # Try alternative: use echo and pipe
                try:
                    logger.info("Trying alternative Piper invocation method...")
                    result = subprocess.run(
                        f'echo "{text}" | piper --model {model_path} --output_file {output_file}',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0 and output_file.exists():
                        logger.info(f"TTS output saved (alternative method): {output_file}")
                        return output_file
                except Exception as alt_error:
                    logger.error(f"Alternative method also failed: {alt_error}")
                return None
            
            if output_file.exists():
                logger.info(f"TTS output saved: {output_file}")
                return output_file
            else:
                logger.error("TTS output file not created")
                return None
                
        except FileNotFoundError:
            logger.error("Piper TTS not found. Please install piper-tts.")
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
