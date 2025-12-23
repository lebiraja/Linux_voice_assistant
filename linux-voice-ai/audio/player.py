"""Audio playback module for Linux Voice AI Assistant."""

import sounddevice as sd
import soundfile as sf
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioPlayer:
    """Handles audio playback through speakers."""
    
    def __init__(self, sample_rate=22050):
        """
        Initialize the audio player.
        
        Args:
            sample_rate: Default sample rate for playback
        """
        self.sample_rate = sample_rate
        logger.info(f"AudioPlayer initialized: {sample_rate}Hz")
    
    def play_file(self, audio_file):
        """
        Play an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            bool: True if playback successful, False otherwise
        """
        audio_file = Path(audio_file)
        
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_file}")
            return False
        
        try:
            # Read audio file
            data, sample_rate = sf.read(audio_file)
            
            # Play audio
            sd.play(data, sample_rate)
            sd.wait()  # Wait until playback is finished
            
            logger.info(f"Played audio file: {audio_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def play_array(self, audio_data, sample_rate=None):
        """
        Play audio from numpy array.
        
        Args:
            audio_data: Numpy array of audio data
            sample_rate: Sample rate of the audio data
            
        Returns:
            bool: True if playback successful, False otherwise
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
        
        try:
            sd.play(audio_data, sample_rate)
            sd.wait()
            
            logger.info("Played audio array")
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio array: {e}")
            return False
    
    def stop(self):
        """Stop any currently playing audio."""
        try:
            sd.stop()
            logger.info("Audio playback stopped")
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")
