"""
Unit tests for configuration management.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from utils.config import Config, ConfigManager, AudioConfig, APIConfig, AppConfig


class TestAudioConfig:
    """Test AudioConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = AudioConfig()
        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.chunk_size == 1024
        assert config.format == "wav"
        assert config.max_duration == 300
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = AudioConfig(
            sample_rate=44100,
            channels=2,
            chunk_size=2048,
            format="mp3",
            max_duration=600
        )
        assert config.sample_rate == 44100
        assert config.channels == 2
        assert config.chunk_size == 2048
        assert config.format == "mp3"
        assert config.max_duration == 600


class TestAPIConfig:
    """Test APIConfig dataclass."""
    
    def test_default_values(self):
        """Test default API configuration values."""
        config = APIConfig()
        assert config.openai_api_key == ""
        assert config.whisper_model == "whisper-1"
        assert config.gpt_model == "gpt-3.5-turbo"
        assert config.max_retries == 3
        assert config.timeout == 30
        assert config.rate_limit_delay == 1.0


class TestConfig:
    """Test main Config class."""
    
    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = Config(
            api=APIConfig(openai_api_key="test-key"),
            audio=AudioConfig(sample_rate=16000, channels=1)
        )
        # Should not raise any exceptions
        assert config.api.openai_api_key == "test-key"
    
    def test_config_validation_invalid_sample_rate(self):
        """Test validation with invalid sample rate."""
        with pytest.raises(ValueError, match="Sample rate must be positive"):
            Config(audio=AudioConfig(sample_rate=-1))
    
    def test_config_validation_invalid_channels(self):
        """Test validation with invalid channels."""
        with pytest.raises(ValueError, match="Channels must be 1 \\(mono\\) or 2 \\(stereo\\)"):
            Config(audio=AudioConfig(channels=3))
    
    def test_config_validation_invalid_retries(self):
        """Test validation with invalid max retries."""
        with pytest.raises(ValueError, match="Max retries cannot be negative"):
            Config(api=APIConfig(max_retries=-1))


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_init(self, temp_dir):
        """Test ConfigManager initialization."""
        manager = ConfigManager(str(temp_dir))
        assert manager.config_dir == temp_dir
        assert manager._config is None
    
    def test_load_config_from_env(self, monkeypatch):
        """Test loading configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "env-test-key")
        monkeypatch.setenv("SAMPLE_RATE", "44100")
        monkeypatch.setenv("WHISPER_MODEL", "whisper-large")
        monkeypatch.setenv("DEBUG", "true")
        
        manager = ConfigManager()
        config = manager.load_config()
        
        assert config.api.openai_api_key == "env-test-key"
        assert config.audio.sample_rate == 44100
        assert config.api.whisper_model == "whisper-large"
        assert config.app.debug is True
    
    def test_parse_window_size_valid(self):
        """Test parsing valid window size."""
        manager = ConfigManager()
        size = manager._parse_window_size("800x600")
        assert size == (800, 600)
    
    def test_parse_window_size_invalid(self):
        """Test parsing invalid window size."""
        manager = ConfigManager()
        size = manager._parse_window_size("invalid")
        assert size == (600, 400)  # Default size
    
    def test_get_config_lazy_loading(self):
        """Test lazy loading of configuration."""
        manager = ConfigManager()
        assert manager._config is None
        
        config = manager.get_config()
        assert manager._config is not None
        assert isinstance(config, Config)
        
        # Second call should return same instance
        config2 = manager.get_config()
        assert config is config2
    
    def test_create_temp_dir(self, temp_dir, monkeypatch):
        """Test temporary directory creation."""
        temp_path = temp_dir / "test_temp"
        monkeypatch.setenv("TEMP_DIR", str(temp_path))
        
        manager = ConfigManager()
        created_path = manager.create_temp_dir()
        
        assert created_path.exists()
        assert created_path.is_dir()


@pytest.mark.unit
class TestConfigIntegration:
    """Integration tests for configuration system."""
    
    def test_full_config_loading_cycle(self, temp_dir, monkeypatch):
        """Test complete configuration loading cycle."""
        # Create .env file
        env_file = temp_dir / ".env"
        env_content = """
OPENAI_API_KEY=integration-test-key
SAMPLE_RATE=22050
CHANNELS=2
WHISPER_MODEL=whisper-large
DEBUG=true
LOG_LEVEL=DEBUG
WINDOW_SIZE=1024x768
"""
        env_file.write_text(env_content.strip())
        
        # Set up manager
        manager = ConfigManager(str(temp_dir))
        config = manager.load_config()
        
        # Verify all settings loaded correctly
        assert config.api.openai_api_key == "integration-test-key"
        assert config.audio.sample_rate == 22050
        assert config.audio.channels == 2
        assert config.api.whisper_model == "whisper-large"
        assert config.app.debug is True
        assert config.app.log_level == "DEBUG"
        assert config.app.window_size == (1024, 768)
