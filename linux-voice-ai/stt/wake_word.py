"""
Wake Word Detection Module
Uses OpenWakeWord for hands-free voice activation with "Hey JARVIS"
"""

import logging
import threading
import queue
import numpy as np
from typing import Callable, Optional

logger = logging.getLogger(__name__)

# Check if OpenWakeWord is available
try:
    import openwakeword
    from openwakeword.model import Model
    OPENWAKEWORD_AVAILABLE = True
except ImportError:
    OPENWAKEWORD_AVAILABLE = False
    logger.warning("OpenWakeWord not installed. Run: pip install openwakeword")


class WakeWordDetector:
    """
    Detects wake words using OpenWakeWord.
    
    Supports continuous listening for hands-free activation.
    Default wake word is "Hey JARVIS".
    """
    
    def __init__(self, 
                 model_name: str = "hey_jarvis",
                 threshold: float = 0.5,
                 chunk_size: int = 1280,
                 sample_rate: int = 16000):
        """
        Initialize wake word detector.
        
        Args:
            model_name: Pre-trained model name (hey_jarvis, alexa, hey_mycroft)
            threshold: Detection threshold (0.0-1.0)
            chunk_size: Audio chunk size for processing
            sample_rate: Audio sample rate (must be 16000 for OpenWakeWord)
        """
        self.model_name = model_name
        self.threshold = threshold
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        
        self.model = None
        self.is_listening = False
        self._listen_thread = None
        self._audio_queue = queue.Queue()
        self._callback = None
        
        if not OPENWAKEWORD_AVAILABLE:
            logger.error("OpenWakeWord not available. Wake word detection disabled.")
            return
        
        # Initialize the model
        try:
            # OpenWakeWord will load all pre-trained models if no paths specified
            # We specify an empty list to load default models including hey_jarvis
            self.model = Model(
                vad_threshold=0.0
            )
            logger.info(f"Wake word detector initialized: '{model_name}' (threshold: {threshold})")
        except Exception as e:
            logger.error(f"Failed to initialize wake word model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if wake word detection is available."""
        return OPENWAKEWORD_AVAILABLE and self.model is not None
    
    def detect(self, audio_chunk: np.ndarray) -> bool:
        """
        Check if wake word is detected in audio chunk.
        
        Args:
            audio_chunk: Numpy array of audio data (int16 or float32)
            
        Returns:
            bool: True if wake word detected
        """
        if not self.is_available():
            return False
        
        try:
            # Convert to int16 if needed
            if audio_chunk.dtype == np.float32:
                audio_chunk = (audio_chunk * 32767).astype(np.int16)
            
            # Run prediction
            prediction = self.model.predict(audio_chunk)
            
            # Check if any wake word exceeds threshold
            for word, score in prediction.items():
                if score > self.threshold:
                    logger.info(f"Wake word detected: '{word}' (score: {score:.2f})")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Wake word detection error: {e}")
            return False
    
    def start_listening(self, callback: Callable[[], None]) -> bool:
        """
        Start continuous wake word listening in background.
        
        Args:
            callback: Function to call when wake word is detected
            
        Returns:
            bool: True if started successfully
        """
        if not self.is_available():
            logger.error("Cannot start listening - wake word not available")
            return False
        
        if self.is_listening:
            logger.warning("Already listening for wake word")
            return True
        
        self._callback = callback
        self.is_listening = True
        
        # Start listening thread
        self._listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True,
            name="WakeWordListener"
        )
        self._listen_thread.start()
        
        logger.info(f"Started listening for wake word: '{self.model_name}'")
        return True
    
    def stop_listening(self):
        """Stop wake word listening."""
        self.is_listening = False
        
        if self._listen_thread:
            self._listen_thread.join(timeout=2.0)
            self._listen_thread = None
        
        logger.info("Stopped wake word listening")
    
    def _listen_loop(self):
        """Background thread for continuous wake word listening."""
        import sounddevice as sd
        
        try:
            # Open audio stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                blocksize=self.chunk_size,
                callback=self._audio_callback
            ):
                while self.is_listening:
                    try:
                        # Get audio chunk from queue
                        audio_chunk = self._audio_queue.get(timeout=0.5)
                        
                        # Check for wake word
                        if self.detect(audio_chunk):
                            if self._callback:
                                logger.info("Wake word detected! Triggering callback...")
                                # Reset model to avoid multiple triggers
                                self.model.reset()
                                # Call the callback
                                self._callback()
                    except queue.Empty:
                        continue
                        
        except Exception as e:
            logger.error(f"Wake word listen loop error: {e}", exc_info=True)
            self.is_listening = False
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream - adds chunks to queue."""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        if self.is_listening:
            # Copy audio data and add to queue
            self._audio_queue.put(indata.copy().flatten())
    
    def reset(self):
        """Reset the wake word model state."""
        if self.model:
            self.model.reset()
            logger.debug("Wake word model reset")


class WakeWordManager:
    """
    Manages wake word detection with UI integration.
    
    Provides high-level control for wake word + hotkey hybrid mode.
    """
    
    def __init__(self, config: dict, on_wake: Callable[[], None]):
        """
        Initialize wake word manager.
        
        Args:
            config: Wake word configuration dict
            on_wake: Callback when wake word detected
        """
        self.config = config
        self.on_wake = on_wake
        self.detector = None
        self.enabled = config.get('enabled', False)
        
        if self.enabled:
            self.detector = WakeWordDetector(
                model_name=config.get('model', 'hey_jarvis'),
                threshold=config.get('threshold', 0.5),
                chunk_size=config.get('chunk_size', 1280)
            )
    
    def start(self) -> bool:
        """Start wake word detection."""
        if not self.enabled or not self.detector:
            return False
        
        return self.detector.start_listening(self.on_wake)
    
    def stop(self):
        """Stop wake word detection."""
        if self.detector:
            self.detector.stop_listening()
    
    def is_available(self) -> bool:
        """Check if wake word is available and enabled."""
        return self.enabled and self.detector and self.detector.is_available()
    
    def toggle(self) -> bool:
        """Toggle wake word detection on/off."""
        if self.detector and self.detector.is_listening:
            self.stop()
            return False
        else:
            return self.start()
