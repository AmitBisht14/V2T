"""
Configuration Management Module

Handles application settings, environment variables, and configuration loading.
"""

import os
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class AudioConfig:
    """Audio processing configuration."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format: str = "wav"
    max_duration: int = 300  # 5 minutes max


@dataclass
class APIConfig:
    """API configuration for OpenAI services."""
    openai_api_key: str = ""
    whisper_model: str = "whisper-1"
    gpt_model: str = "gpt-3.5-turbo"
    max_retries: int = 3
    timeout: int = 30
    rate_limit_delay: float = 1.0


@dataclass
class AppConfig:
    """Application configuration."""
    debug: bool = False
    log_level: str = "INFO"
    temp_dir: str = "./temp"
    window_title: str = "V2T - Voice to Text"
    window_size: tuple = (600, 400)
    theme: str = "default"


@dataclass
class Config:
    """Main configuration class containing all settings."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    api: APIConfig = field(default_factory=APIConfig)
    app: AppConfig = field(default_factory=AppConfig)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        if not self.api.openai_api_key:
            logger.warning("OpenAI API key not configured")
        
        if self.audio.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        if self.audio.channels not in [1, 2]:
            raise ValueError("Channels must be 1 (mono) or 2 (stereo)")
        
        if self.api.max_retries < 0:
            raise ValueError("Max retries cannot be negative")


class ConfigManager:
    """Manages application configuration loading and access."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._config: Optional[Config] = None
        
    def load_config(self, env_file: str = ".env") -> Config:
        """
        Load configuration from environment variables and .env file.
        
        Args:
            env_file: Name of the environment file
            
        Returns:
            Loaded configuration
        """
        env_path = self.config_dir / env_file
        
        # Load .env file if it exists and dotenv is available
        if load_dotenv and env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {env_path}")
        elif env_path.exists():
            logger.warning("python-dotenv not installed, .env file ignored")
        
        # Create configuration from environment variables
        audio_config = AudioConfig(
            sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
            channels=int(os.getenv("CHANNELS", "1")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1024")),
            format=os.getenv("AUDIO_FORMAT", "wav"),
            max_duration=int(os.getenv("MAX_DURATION", "300"))
        )
        
        api_config = APIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            whisper_model=os.getenv("WHISPER_MODEL", "whisper-1"),
            gpt_model=os.getenv("GPT_MODEL", "gpt-3.5-turbo"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            timeout=int(os.getenv("TIMEOUT", "30")),
            rate_limit_delay=float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
        )
        
        app_config = AppConfig(
            debug=os.getenv("DEBUG", "False").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            temp_dir=os.getenv("TEMP_DIR", "./temp"),
            window_title=os.getenv("WINDOW_TITLE", "V2T - Voice to Text"),
            window_size=self._parse_window_size(os.getenv("WINDOW_SIZE", "600x400")),
            theme=os.getenv("THEME", "default")
        )
        
        self._config = Config(
            audio=audio_config,
            api=api_config,
            app=app_config
        )
        
        logger.info("Configuration loaded successfully")
        return self._config
    
    def get_config(self) -> Config:
        """
        Get the current configuration, loading it if necessary.
        
        Returns:
            Current configuration
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def _parse_window_size(self, size_str: str) -> tuple:
        """Parse window size string like '600x400' into tuple."""
        try:
            width, height = size_str.split('x')
            return (int(width), int(height))
        except (ValueError, AttributeError):
            logger.warning(f"Invalid window size format: {size_str}, using default")
            return (600, 400)
    
    def create_temp_dir(self) -> Path:
        """Create temporary directory if it doesn't exist."""
        temp_path = Path(self.get_config().app.temp_dir)
        temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config_manager.get_config()


def reload_config() -> Config:
    """Reload configuration from files."""
    return config_manager.load_config()
