"""
Custom Exception Classes for V2T Application

Defines application-specific exceptions for better error handling and debugging.
"""

from typing import Optional, Any


class V2TException(Exception):
    """
    Base exception class for all V2T application errors.
    
    All custom exceptions should inherit from this class to maintain
    a consistent exception hierarchy.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Any] = None):
        """
        Initialize V2T exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional additional details about the error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AudioError(V2TException):
    """
    Exception raised for audio-related errors.
    
    This includes microphone access issues, audio processing failures,
    device connection problems, etc.
    """
    
    def __init__(self, message: str, device_info: Optional[dict] = None, **kwargs):
        """
        Initialize audio error.
        
        Args:
            message: Error message
            device_info: Optional information about the audio device
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.device_info = device_info


class MicrophoneError(AudioError):
    """Exception raised for microphone-specific errors."""
    pass


class AudioProcessingError(AudioError):
    """Exception raised during audio processing operations."""
    pass


class AudioDeviceError(AudioError):
    """Exception raised for audio device management errors."""
    pass


class APIError(V2TException):
    """
    Exception raised for API-related errors.
    
    This includes network issues, authentication failures,
    rate limiting, and API response errors.
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[dict] = None,
        **kwargs
    ):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: API response data if available
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data


class OpenAIError(APIError):
    """Exception raised for OpenAI API specific errors."""
    pass


class WhisperError(OpenAIError):
    """Exception raised for Whisper API specific errors."""
    pass


class GPTError(OpenAIError):
    """Exception raised for GPT API specific errors."""
    pass


class NetworkError(APIError):
    """Exception raised for network connectivity issues."""
    pass


class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Exception raised for API authentication failures."""
    pass


class ConfigurationError(V2TException):
    """
    Exception raised for configuration-related errors.
    
    This includes missing configuration values, invalid settings,
    and configuration file issues.
    """
    pass


class ValidationError(V2TException):
    """Exception raised for data validation errors."""
    pass


class FileError(V2TException):
    """
    Exception raised for file operation errors.
    
    This includes file not found, permission denied, and I/O errors.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        """
        Initialize file error.
        
        Args:
            message: Error message
            file_path: Path to the file that caused the error
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.file_path = file_path


class GUIError(V2TException):
    """Exception raised for GUI-related errors."""
    pass


class TranscriptionError(V2TException):
    """
    Exception raised during transcription process.
    
    This is a high-level exception that can wrap other errors
    that occur during the complete transcription workflow.
    """
    
    def __init__(self, message: str, stage: Optional[str] = None, **kwargs):
        """
        Initialize transcription error.
        
        Args:
            message: Error message
            stage: Stage of transcription where error occurred
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.stage = stage


# Error code constants for programmatic error handling
class ErrorCodes:
    """Constants for error codes used throughout the application."""
    
    # Audio errors
    MICROPHONE_NOT_FOUND = "AUDIO_001"
    MICROPHONE_PERMISSION_DENIED = "AUDIO_002"
    AUDIO_DEVICE_BUSY = "AUDIO_003"
    AUDIO_FORMAT_UNSUPPORTED = "AUDIO_004"
    RECORDING_FAILED = "AUDIO_005"
    
    # API errors
    API_KEY_MISSING = "API_001"
    API_KEY_INVALID = "API_002"
    NETWORK_TIMEOUT = "API_003"
    RATE_LIMIT_EXCEEDED = "API_004"
    API_QUOTA_EXCEEDED = "API_005"
    INVALID_AUDIO_FORMAT = "API_006"
    
    # Configuration errors
    CONFIG_FILE_NOT_FOUND = "CONFIG_001"
    CONFIG_INVALID_FORMAT = "CONFIG_002"
    CONFIG_MISSING_REQUIRED = "CONFIG_003"
    
    # File errors
    FILE_NOT_FOUND = "FILE_001"
    FILE_PERMISSION_DENIED = "FILE_002"
    DISK_SPACE_INSUFFICIENT = "FILE_003"
    
    # GUI errors
    WINDOW_CREATION_FAILED = "GUI_001"
    WIDGET_INITIALIZATION_FAILED = "GUI_002"


def handle_exception(func):
    """
    Decorator for consistent exception handling and logging.
    
    This decorator can be used to wrap functions that should
    have consistent error handling behavior.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except V2TException:
            # Re-raise V2T exceptions as-is
            raise
        except Exception as e:
            # Wrap other exceptions in V2TException
            raise V2TException(
                f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                details={"function": func.__name__, "original_error": str(e)}
            ) from e
    
    return wrapper
