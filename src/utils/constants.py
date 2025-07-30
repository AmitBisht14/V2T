"""
Application Constants

Defines all constant values used throughout the V2T application.
"""

from pathlib import Path


# Application Information
APP_NAME = "V2T"
APP_FULL_NAME = "Voice to Text Desktop Application"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Developer"
APP_DESCRIPTION = "Convert speech to text using OpenAI APIs"


# File and Directory Constants
DEFAULT_CONFIG_DIR = "config"
DEFAULT_LOGS_DIR = "logs"
DEFAULT_TEMP_DIR = "temp"
DEFAULT_ASSETS_DIR = "assets"

# Configuration Files
ENV_FILE = ".env"
ENV_EXAMPLE_FILE = ".env.example"
CONFIG_FILE = "config.json"
LOG_CONFIG_FILE = "logging.conf"

# Log Files
APP_LOG_FILE = "app.log"
ERROR_LOG_FILE = "error.log"
AUDIO_LOG_FILE = "audio.log"
API_LOG_FILE = "api.log"


# Audio Constants
class AudioConstants:
    """Audio processing constants."""
    
    # Sample rates (Hz)
    SAMPLE_RATE_8K = 8000
    SAMPLE_RATE_16K = 16000
    SAMPLE_RATE_44K = 44100
    SAMPLE_RATE_48K = 48000
    
    DEFAULT_SAMPLE_RATE = SAMPLE_RATE_16K
    
    # Audio formats
    FORMAT_WAV = "wav"
    FORMAT_MP3 = "mp3"
    FORMAT_M4A = "m4a"
    FORMAT_FLAC = "flac"
    
    DEFAULT_FORMAT = FORMAT_WAV
    SUPPORTED_FORMATS = [FORMAT_WAV, FORMAT_MP3, FORMAT_M4A, FORMAT_FLAC]
    
    # Channels
    MONO = 1
    STEREO = 2
    DEFAULT_CHANNELS = MONO
    
    # Buffer settings
    DEFAULT_CHUNK_SIZE = 1024
    MIN_CHUNK_SIZE = 512
    MAX_CHUNK_SIZE = 8192
    
    # Recording limits
    MIN_RECORDING_DURATION = 0.1  # seconds
    MAX_RECORDING_DURATION = 300  # 5 minutes
    DEFAULT_MAX_DURATION = 60     # 1 minute
    
    # Audio quality
    BITS_PER_SAMPLE_16 = 16
    BITS_PER_SAMPLE_24 = 24
    DEFAULT_BITS_PER_SAMPLE = BITS_PER_SAMPLE_16
    
    # File size limits (bytes)
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB (OpenAI limit)
    RECOMMENDED_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# API Constants
class APIConstants:
    """API-related constants."""
    
    # OpenAI API
    OPENAI_BASE_URL = "https://api.openai.com/v1"
    WHISPER_ENDPOINT = "/audio/transcriptions"
    GPT_ENDPOINT = "/chat/completions"
    
    # Models
    WHISPER_MODEL_TINY = "whisper-1"
    WHISPER_MODEL_BASE = "whisper-1"
    WHISPER_MODEL_SMALL = "whisper-1"
    WHISPER_MODEL_MEDIUM = "whisper-1"
    WHISPER_MODEL_LARGE = "whisper-1"
    
    DEFAULT_WHISPER_MODEL = WHISPER_MODEL_TINY
    
    GPT_MODEL_3_5_TURBO = "gpt-3.5-turbo"
    GPT_MODEL_4 = "gpt-4"
    GPT_MODEL_4_TURBO = "gpt-4-turbo-preview"
    
    DEFAULT_GPT_MODEL = GPT_MODEL_3_5_TURBO
    
    # Request settings
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RATE_LIMIT_DELAY = 1.0  # seconds
    
    # Response formats
    RESPONSE_FORMAT_JSON = "json"
    RESPONSE_FORMAT_TEXT = "text"
    RESPONSE_FORMAT_SRT = "srt"
    RESPONSE_FORMAT_VTT = "vtt"
    
    DEFAULT_RESPONSE_FORMAT = RESPONSE_FORMAT_TEXT
    
    # Rate limiting
    REQUESTS_PER_MINUTE = 50
    TOKENS_PER_MINUTE = 40000


# GUI Constants
class GUIConstants:
    """GUI-related constants."""
    
    # Window settings
    DEFAULT_WINDOW_WIDTH = 600
    DEFAULT_WINDOW_HEIGHT = 400
    MIN_WINDOW_WIDTH = 400
    MIN_WINDOW_HEIGHT = 300
    MAX_WINDOW_WIDTH = 1200
    MAX_WINDOW_HEIGHT = 800
    
    DEFAULT_WINDOW_TITLE = "V2T - Voice to Text"
    
    # Colors (Hex values)
    PRIMARY_COLOR = "#2563eb"      # Blue
    SECONDARY_COLOR = "#64748b"    # Slate
    SUCCESS_COLOR = "#10b981"      # Green
    WARNING_COLOR = "#f59e0b"      # Amber
    ERROR_COLOR = "#ef4444"        # Red
    BACKGROUND_COLOR = "#f8fafc"   # Light gray
    TEXT_COLOR = "#1e293b"         # Dark slate
    
    # Button states
    BUTTON_NORMAL = "#e2e8f0"
    BUTTON_HOVER = "#cbd5e1"
    BUTTON_ACTIVE = "#94a3b8"
    BUTTON_DISABLED = "#f1f5f9"
    
    # Fonts
    DEFAULT_FONT_FAMILY = "Segoe UI"
    DEFAULT_FONT_SIZE = 10
    TITLE_FONT_SIZE = 14
    BUTTON_FONT_SIZE = 9
    STATUS_FONT_SIZE = 8
    
    # Spacing
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20
    
    MARGIN_SMALL = 5
    MARGIN_MEDIUM = 10
    MARGIN_LARGE = 20
    
    # Widget dimensions
    BUTTON_HEIGHT = 30
    BUTTON_WIDTH = 100
    TEXT_AREA_HEIGHT = 200
    STATUS_BAR_HEIGHT = 25
    
    # Animation
    FADE_DURATION = 200  # milliseconds
    BUTTON_PRESS_DURATION = 100
    
    # Icons (if using icon files)
    ICON_SIZE_SMALL = 16
    ICON_SIZE_MEDIUM = 24
    ICON_SIZE_LARGE = 32


# Status Messages
class StatusMessages:
    """Status and user feedback messages."""
    
    # Application states
    READY = "Ready"
    RECORDING = "Recording..."
    PROCESSING = "Processing audio..."
    TRANSCRIBING = "Transcribing..."
    CLEANING = "Cleaning text..."
    COMPLETED = "Transcription completed"
    ERROR = "Error occurred"
    
    # Recording states
    RECORDING_STARTED = "Recording started"
    RECORDING_STOPPED = "Recording stopped"
    RECORDING_PAUSED = "Recording paused"
    RECORDING_RESUMED = "Recording resumed"
    
    # API states
    CONNECTING_API = "Connecting to API..."
    API_REQUEST_SENT = "Request sent to API"
    API_RESPONSE_RECEIVED = "Response received from API"
    API_ERROR = "API request failed"
    
    # File operations
    FILE_SAVED = "File saved successfully"
    FILE_LOADED = "File loaded successfully"
    FILE_ERROR = "File operation failed"
    
    # Configuration
    CONFIG_LOADED = "Configuration loaded"
    CONFIG_SAVED = "Configuration saved"
    CONFIG_ERROR = "Configuration error"


# Keyboard Shortcuts
class KeyboardShortcuts:
    """Keyboard shortcut definitions."""
    
    # Recording controls
    START_STOP_RECORDING = "<F1>"
    PAUSE_RESUME_RECORDING = "<F2>"
    
    # File operations
    NEW_FILE = "<Control-n>"
    OPEN_FILE = "<Control-o>"
    SAVE_FILE = "<Control-s>"
    SAVE_AS = "<Control-Shift-s>"
    
    # Edit operations
    COPY = "<Control-c>"
    PASTE = "<Control-v>"
    CUT = "<Control-x>"
    SELECT_ALL = "<Control-a>"
    UNDO = "<Control-z>"
    REDO = "<Control-y>"
    
    # Application
    QUIT = "<Control-q>"
    SETTINGS = "<Control-comma>"
    HELP = "<F1>"


# File Extensions and Filters
class FileFilters:
    """File dialog filters."""
    
    AUDIO_FILES = [
        ("Audio Files", "*.wav *.mp3 *.m4a *.flac"),
        ("WAV Files", "*.wav"),
        ("MP3 Files", "*.mp3"),
        ("M4A Files", "*.m4a"),
        ("FLAC Files", "*.flac"),
        ("All Files", "*.*")
    ]
    
    TEXT_FILES = [
        ("Text Files", "*.txt"),
        ("All Files", "*.*")
    ]
    
    CONFIG_FILES = [
        ("Configuration Files", "*.json *.ini *.conf"),
        ("JSON Files", "*.json"),
        ("INI Files", "*.ini"),
        ("All Files", "*.*")
    ]


# Regular Expressions
class RegexPatterns:
    """Common regex patterns used in the application."""
    
    # Audio file validation
    AUDIO_FILE_PATTERN = r'\.(wav|mp3|m4a|flac)$'
    
    # API key validation (basic format check)
    OPENAI_API_KEY_PATTERN = r'^sk-[A-Za-z0-9]{48}$'
    
    # Window size validation
    WINDOW_SIZE_PATTERN = r'^\d+x\d+$'
    
    # Time format (HH:MM:SS)
    TIME_FORMAT_PATTERN = r'^\d{2}:\d{2}:\d{2}$'


# Error Messages
class ErrorMessages:
    """Standard error messages."""
    
    # Audio errors
    MICROPHONE_NOT_AVAILABLE = "Microphone not available or access denied"
    AUDIO_DEVICE_ERROR = "Audio device error occurred"
    RECORDING_FAILED = "Failed to start recording"
    AUDIO_PROCESSING_FAILED = "Audio processing failed"
    
    # API errors
    API_KEY_MISSING = "OpenAI API key not configured"
    API_KEY_INVALID = "Invalid OpenAI API key"
    NETWORK_ERROR = "Network connection error"
    API_QUOTA_EXCEEDED = "API quota exceeded"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded, please wait"
    
    # File errors
    FILE_NOT_FOUND = "File not found"
    FILE_ACCESS_DENIED = "Access denied to file"
    DISK_SPACE_LOW = "Insufficient disk space"
    
    # Configuration errors
    CONFIG_LOAD_FAILED = "Failed to load configuration"
    CONFIG_SAVE_FAILED = "Failed to save configuration"
    INVALID_CONFIGURATION = "Invalid configuration values"


# Success Messages
class SuccessMessages:
    """Standard success messages."""
    
    TRANSCRIPTION_COMPLETED = "Transcription completed successfully"
    FILE_SAVED_SUCCESSFULLY = "File saved successfully"
    CONFIGURATION_SAVED = "Configuration saved successfully"
    RECORDING_SAVED = "Recording saved successfully"


# Development Constants
class DevConstants:
    """Constants used during development and testing."""
    
    # Test data
    TEST_AUDIO_DURATION = 5.0  # seconds
    TEST_SAMPLE_TEXT = "This is a test transcription."
    
    # Debug settings
    DEBUG_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    PRODUCTION_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
    # Performance monitoring
    PERFORMANCE_THRESHOLD_MS = 1000  # 1 second
    MEMORY_USAGE_THRESHOLD_MB = 100  # 100 MB
