"""
Audio Recording Module

Handles microphone access, audio capture, and recording functionality.
"""

import os
import wave
import threading
import time
from pathlib import Path
from typing import Optional, Callable, Any
from dataclasses import dataclass

# PyAudio import with fallback for development
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    pyaudio = None
    PYAUDIO_AVAILABLE = False

from ..utils.logging_config import get_logger
from ..utils.config import get_config
from ..utils.constants import AudioConstants, StatusMessages, ErrorMessages
from ..utils.exceptions import (
    AudioError, MicrophoneError, AudioProcessingError, 
    AudioDeviceError, FileError
)

logger = get_logger(__name__)


@dataclass
class RecordingState:
    """Represents the current state of audio recording."""
    is_recording: bool = False
    is_paused: bool = False
    start_time: Optional[float] = None
    duration: float = 0.0
    file_path: Optional[str] = None
    frames_recorded: int = 0


class AudioRecorder:
    """
    Handles audio recording from microphone using PyAudio.
    
    Provides methods for starting, stopping, and managing audio recording
    with proper error handling and device management.
    """
    
    def __init__(self, device_index: Optional[int] = None):
        """
        Initialize the AudioRecorder.
        
        Args:
            device_index: Optional specific audio device index to use
            
        Raises:
            AudioError: If PyAudio is not available or initialization fails
        """
        if not PYAUDIO_AVAILABLE:
            raise AudioError(
                "PyAudio is not available. Please install PyAudio for audio recording.",
                error_code="PYAUDIO_NOT_AVAILABLE"
            )
        
        self.config = get_config()
        self.device_index = device_index
        self.pyaudio_instance: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.recording_thread: Optional[threading.Thread] = None
        self.state = RecordingState()
        self.audio_frames: list = []
        self._stop_event = threading.Event()
        
        # Callbacks
        self.on_recording_started: Optional[Callable] = None
        self.on_recording_stopped: Optional[Callable] = None
        self.on_recording_error: Optional[Callable] = None
        self.on_audio_data: Optional[Callable[[bytes], None]] = None
        
        logger.info("AudioRecorder initialized")
    
    def initialize_pyaudio(self) -> None:
        """
        Initialize PyAudio instance and verify microphone access.
        
        Raises:
            MicrophoneError: If microphone initialization fails
            AudioDeviceError: If no audio devices are available
        """
        try:
            if self.pyaudio_instance is None:
                self.pyaudio_instance = pyaudio.PyAudio()
                logger.info("PyAudio instance created successfully")
            
            # Verify device access
            device_count = self.pyaudio_instance.get_device_count()
            if device_count == 0:
                raise AudioDeviceError(
                    "No audio devices found",
                    error_code="NO_AUDIO_DEVICES"
                )
            
            # Find suitable input device if not specified
            if self.device_index is None:
                self.device_index = self._find_default_input_device()
            
            # Verify the selected device
            self._verify_device_access()
            
            logger.info(f"PyAudio initialized with device index: {self.device_index}")
            
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
            if isinstance(e, (AudioError, MicrophoneError, AudioDeviceError)):
                raise
            raise MicrophoneError(
                f"Failed to initialize microphone: {str(e)}",
                error_code="MICROPHONE_INIT_FAILED"
            ) from e
    
    def _find_default_input_device(self) -> int:
        """
        Find the default input device.
        
        Returns:
            Device index of the default input device
            
        Raises:
            AudioDeviceError: If no suitable input device is found
        """
        try:
            # Try to get the default input device
            default_device = self.pyaudio_instance.get_default_input_device_info()
            device_index = default_device['index']
            
            logger.info(f"Found default input device: {default_device['name']}")
            return device_index
            
        except OSError:
            # Fallback: search for any input device
            logger.warning("No default input device found, searching for alternatives")
            
            for i in range(self.pyaudio_instance.get_device_count()):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    logger.info(f"Using input device: {device_info['name']}")
                    return i
            
            raise AudioDeviceError(
                "No suitable input device found",
                error_code="NO_INPUT_DEVICE"
            )
    
    def _verify_device_access(self) -> None:
        """
        Verify that we can access the selected audio device.
        
        Raises:
            MicrophoneError: If device access verification fails
        """
        try:
            device_info = self.pyaudio_instance.get_device_info_by_index(self.device_index)
            
            # Check if device supports input
            if device_info['maxInputChannels'] == 0:
                raise MicrophoneError(
                    f"Device '{device_info['name']}' does not support audio input",
                    error_code="DEVICE_NO_INPUT",
                    device_info=device_info
                )
            
            # Try to create a test stream to verify access
            test_stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.config.audio.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.config.audio.chunk_size,
                start=False
            )
            test_stream.close()
            
            logger.info(f"Device access verified: {device_info['name']}")
            
        except Exception as e:
            logger.error(f"Device access verification failed: {e}")
            raise MicrophoneError(
                f"Cannot access microphone device: {str(e)}",
                error_code="DEVICE_ACCESS_DENIED",
                device_info=device_info if 'device_info' in locals() else None
            ) from e
    
    def get_device_info(self) -> dict:
        """
        Get information about the current audio device.
        
        Returns:
            Dictionary containing device information
            
        Raises:
            AudioError: If PyAudio is not initialized
        """
        if self.pyaudio_instance is None:
            raise AudioError("PyAudio not initialized")
        
        if self.device_index is None:
            raise AudioError("No device selected")
        
        return self.pyaudio_instance.get_device_info_by_index(self.device_index)
    
    def cleanup(self) -> None:
        """Clean up PyAudio resources."""
        try:
            if self.stream and not self.stream.is_stopped():
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            
            logger.info("AudioRecorder cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize_pyaudio()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


# Utility function for checking PyAudio availability
def is_pyaudio_available() -> bool:
    """
    Check if PyAudio is available for use.
    
    Returns:
        True if PyAudio is available, False otherwise
    """
    return PYAUDIO_AVAILABLE


def get_audio_recorder(device_index: Optional[int] = None) -> AudioRecorder:
    """
    Factory function to create an AudioRecorder instance.
    
    Args:
        device_index: Optional specific audio device index
        
    Returns:
        Configured AudioRecorder instance
        
    Raises:
        AudioError: If PyAudio is not available
    """
    if not PYAUDIO_AVAILABLE:
        raise AudioError(
            ErrorMessages.MICROPHONE_NOT_AVAILABLE,
            error_code="PYAUDIO_NOT_AVAILABLE"
        )
    
    return AudioRecorder(device_index=device_index)
