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
    
    def start_recording(self, output_file: Optional[str] = None) -> str:
        """
        Start audio recording from the microphone.
        
        Args:
            output_file: Optional path for output file. If None, generates temp file.
            
        Returns:
            Path to the recording file
            
        Raises:
            AudioError: If recording is already in progress
            MicrophoneError: If microphone access fails
            FileError: If output file cannot be created
        """
        if self.state.is_recording:
            raise AudioError(
                "Recording is already in progress",
                error_code="RECORDING_IN_PROGRESS"
            )
        
        try:
            # Initialize PyAudio if not already done
            if self.pyaudio_instance is None:
                self.initialize_pyaudio()
            
            # Generate output file path if not provided
            if output_file is None:
                output_file = self._generate_temp_filename()
            
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Reset state
            self.state = RecordingState(
                is_recording=True,
                start_time=time.time(),
                file_path=str(output_path)
            )
            self.audio_frames = []
            self._stop_event.clear()
            
            # Create audio stream
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=self.config.audio.channels,
                rate=self.config.audio.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.config.audio.chunk_size,
                start=False
            )
            
            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._recording_worker,
                daemon=True
            )
            self.recording_thread.start()
            
            # Start the stream
            self.stream.start_stream()
            
            logger.info(f"Recording started: {output_file}")
            
            # Trigger callback
            if self.on_recording_started:
                self.on_recording_started(output_file)
            
            return str(output_path)
            
        except Exception as e:
            # Reset state on error
            self.state.is_recording = False
            logger.error(f"Failed to start recording: {e}")
            
            if isinstance(e, (AudioError, MicrophoneError, FileError)):
                raise
            
            raise MicrophoneError(
                f"Failed to start recording: {str(e)}",
                error_code="RECORDING_START_FAILED"
            ) from e
    
    def _generate_temp_filename(self) -> str:
        """
        Generate a temporary filename for recording.
        
        Returns:
            Path to temporary recording file
        """
        from ..utils.config import config_manager
        
        temp_dir = config_manager.create_temp_dir()
        timestamp = int(time.time())
        filename = f"recording_{timestamp}.wav"
        return str(temp_dir / filename)
    
    def _recording_worker(self) -> None:
        """
        Worker thread for continuous audio recording.
        
        This method runs in a separate thread and continuously reads
        audio data from the microphone stream.
        """
        try:
            logger.debug("Recording worker thread started")
            
            while not self._stop_event.is_set() and self.state.is_recording:
                try:
                    # Check for maximum duration
                    if self.state.start_time:
                        elapsed = time.time() - self.state.start_time
                        if elapsed >= self.config.audio.max_duration:
                            logger.warning(f"Maximum recording duration reached: {self.config.audio.max_duration}s")
                            break
                    
                    # Read audio data
                    if self.stream and self.stream.is_active():
                        try:
                            data = self.stream.read(
                                self.config.audio.chunk_size,
                                exception_on_overflow=False
                            )
                            
                            if data:
                                self.audio_frames.append(data)
                                self.state.frames_recorded += 1
                                
                                # Update duration
                                if self.state.start_time:
                                    self.state.duration = time.time() - self.state.start_time
                                
                                # Trigger data callback
                                if self.on_audio_data:
                                    self.on_audio_data(data)
                                    
                        except Exception as e:
                            if not self._stop_event.is_set():
                                logger.error(f"Error reading audio data: {e}")
                                break
                    else:
                        break
                        
                except Exception as e:
                    logger.error(f"Error in recording worker: {e}")
                    break
            
            logger.debug("Recording worker thread finished")
            
        except Exception as e:
            logger.error(f"Fatal error in recording worker: {e}")
            if self.on_recording_error:
                self.on_recording_error(e)
    
    def stop_recording(self, save_file: bool = True) -> Optional[str]:
        """
        Stop audio recording and optionally save to file.
        
        Args:
            save_file: Whether to save the recorded audio to file
            
        Returns:
            Path to saved file if save_file=True, None otherwise
            
        Raises:
            AudioError: If no recording is in progress
            FileError: If file saving fails
        """
        if not self.state.is_recording:
            raise AudioError(
                "No recording in progress",
                error_code="NO_RECORDING_IN_PROGRESS"
            )
        
        try:
            logger.info("Stopping recording...")
            
            # Signal the recording thread to stop
            self._stop_event.set()
            self.state.is_recording = False
            
            # Stop and close the audio stream
            if self.stream:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5.0)
                if self.recording_thread.is_alive():
                    logger.warning("Recording thread did not finish within timeout")
            
            # Update final duration
            if self.state.start_time:
                self.state.duration = time.time() - self.state.start_time
            
            saved_file = None
            if save_file and self.audio_frames:
                saved_file = self._save_recording()
            
            logger.info(f"Recording stopped. Duration: {self.state.duration:.2f}s, Frames: {self.state.frames_recorded}")
            
            # Trigger callback
            if self.on_recording_stopped:
                self.on_recording_stopped(saved_file, self.state.duration)
            
            return saved_file
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            if isinstance(e, (AudioError, FileError)):
                raise
            
            raise AudioError(
                f"Failed to stop recording: {str(e)}",
                error_code="RECORDING_STOP_FAILED"
            ) from e
        
        finally:
            # Ensure state is reset
            self.state.is_recording = False
    
    def _save_recording(self) -> str:
        """
        Save the recorded audio frames to a WAV file.
        
        Returns:
            Path to the saved file
            
        Raises:
            FileError: If file saving fails
        """
        if not self.audio_frames:
            raise FileError(
                "No audio data to save",
                error_code="NO_AUDIO_DATA"
            )
        
        if not self.state.file_path:
            raise FileError(
                "No output file path specified",
                error_code="NO_OUTPUT_PATH"
            )
        
        try:
            # Ensure output directory exists
            output_path = Path(self.state.file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio data as WAV file
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(self.config.audio.channels)
                wav_file.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
                wav_file.setframerate(self.config.audio.sample_rate)
                wav_file.writeframes(b''.join(self.audio_frames))
            
            # Verify file was created and has content
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise FileError(
                    f"Failed to create audio file: {output_path}",
                    error_code="FILE_CREATION_FAILED",
                    file_path=str(output_path)
                )
            
            file_size = output_path.stat().st_size
            logger.info(f"Audio saved: {output_path} ({file_size} bytes)")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to save recording: {e}")
            if isinstance(e, FileError):
                raise
            
            raise FileError(
                f"Failed to save recording to {self.state.file_path}: {str(e)}",
                error_code="FILE_SAVE_FAILED",
                file_path=self.state.file_path
            ) from e
    
    def pause_recording(self) -> None:
        """
        Pause the current recording.
        
        Raises:
            AudioError: If no recording is in progress or already paused
        """
        if not self.state.is_recording:
            raise AudioError(
                "No recording in progress",
                error_code="NO_RECORDING_IN_PROGRESS"
            )
        
        if self.state.is_paused:
            raise AudioError(
                "Recording is already paused",
                error_code="RECORDING_ALREADY_PAUSED"
            )
        
        try:
            if self.stream and self.stream.is_active():
                self.stream.stop_stream()
            
            self.state.is_paused = True
            logger.info("Recording paused")
            
        except Exception as e:
            logger.error(f"Failed to pause recording: {e}")
            raise AudioError(
                f"Failed to pause recording: {str(e)}",
                error_code="RECORDING_PAUSE_FAILED"
            ) from e
    
    def resume_recording(self) -> None:
        """
        Resume a paused recording.
        
        Raises:
            AudioError: If no recording is in progress or not paused
        """
        if not self.state.is_recording:
            raise AudioError(
                "No recording in progress",
                error_code="NO_RECORDING_IN_PROGRESS"
            )
        
        if not self.state.is_paused:
            raise AudioError(
                "Recording is not paused",
                error_code="RECORDING_NOT_PAUSED"
            )
        
        try:
            if self.stream and not self.stream.is_active():
                self.stream.start_stream()
            
            self.state.is_paused = False
            logger.info("Recording resumed")
            
        except Exception as e:
            logger.error(f"Failed to resume recording: {e}")
            raise AudioError(
                f"Failed to resume recording: {str(e)}",
                error_code="RECORDING_RESUME_FAILED"
            ) from e
    
    def get_recording_info(self) -> dict:
        """
        Get information about the current recording state.
        
        Returns:
            Dictionary containing recording information
        """
        return {
            'is_recording': self.state.is_recording,
            'is_paused': self.state.is_paused,
            'duration': self.state.duration,
            'frames_recorded': self.state.frames_recorded,
            'file_path': self.state.file_path,
            'start_time': self.state.start_time
        }
    
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
