"""Audio recording module for Linux Voice AI Assistant."""

import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Handles audio recording from microphone."""
    
    def __init__(self, sample_rate=16000, channels=1, temp_dir="temp"):
        """
        Initialize the audio recorder.
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1 for mono)
            temp_dir: Directory to store temporary audio files
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
        self.recording = []
        self.is_recording = False
        
        # Set default device to use PulseAudio/pipewire
        try:
            # Try to use 'default' or 'pipewire' device
            devices = sd.query_devices()
            default_input = sd.default.device[0]
            logger.info(f"Using audio input device: {devices[default_input]['name']}")
        except Exception as e:
            logger.warning(f"Could not query audio devices: {e}")
        
        logger.info(f"AudioRecorder initialized: {sample_rate}Hz, {channels} channel(s)")
    
    def start_recording(self):
        """Start recording audio."""
        self.recording = []
        self.is_recording = True
        logger.info("Recording started")
    
    def record_chunk(self, duration=0.1):
        """
        Record a chunk of audio.
        
        Args:
            duration: Duration of chunk in seconds
            
        Returns:
            numpy array of audio data
        """
        if not self.is_recording:
            return None
            
        try:
            audio_chunk = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()
            self.recording.append(audio_chunk)
            return audio_chunk
        except Exception as e:
            logger.error(f"Error recording chunk: {e}")
            return None
    
    def stop_recording(self):
        """
        Stop recording and save to file.
        
        Returns:
            Path to saved audio file
        """
        self.is_recording = False
        
        if not self.recording:
            logger.warning("No audio recorded")
            return None
        
        # Concatenate all chunks
        audio_data = np.concatenate(self.recording, axis=0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.temp_dir / f"recording_{timestamp}.wav"
        
        # Save to WAV file
        try:
            sf.write(filename, audio_data, self.sample_rate)
            logger.info(f"Recording saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving recording: {e}")
            return None
    
    def record_audio(self, duration=5):
        """
        Record audio for a specified duration.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Path to saved audio file
        """
        logger.info(f"Recording for {duration} seconds...")
        
        try:
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                device=None  # Use default device
            )
            sd.wait()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.temp_dir / f"recording_{timestamp}.wav"
            
            # Save to file with explicit format
            sf.write(
                str(filename),  # Convert Path to string
                audio_data,
                self.sample_rate,
                subtype='PCM_16'  # Explicit 16-bit PCM format
            )
            logger.info(f"Recording saved: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error during recording: {e}")
            return None
    
    def cleanup_old_recordings(self, keep_last=10):
        """
        Remove old recording files, keeping only the most recent ones.
        
        Args:
            keep_last: Number of recent recordings to keep
        """
        try:
            recordings = sorted(
                self.temp_dir.glob("recording_*.wav"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            for old_file in recordings[keep_last:]:
                old_file.unlink()
                logger.debug(f"Deleted old recording: {old_file}")
                
        except Exception as e:
            logger.error(f"Error cleaning up recordings: {e}")
