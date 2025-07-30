"""
Pytest configuration and shared fixtures for V2T tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock

# Add src to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import Config, AudioConfig, APIConfig, AppConfig


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return Config(
        audio=AudioConfig(
            sample_rate=16000,
            channels=1,
            chunk_size=1024,
            format="wav",
            max_duration=300
        ),
        api=APIConfig(
            openai_api_key="test-key-123",
            whisper_model="whisper-1",
            gpt_model="gpt-3.5-turbo",
            max_retries=3,
            timeout=30,
            rate_limit_delay=1.0
        ),
        app=AppConfig(
            debug=True,
            log_level="DEBUG",
            temp_dir="./test_temp",
            window_title="V2T Test",
            window_size=(800, 600),
            theme="test"
        )
    )


@pytest.fixture
def mock_audio_data():
    """Create mock audio data for testing."""
    # Simple sine wave data for testing
    import numpy as np
    sample_rate = 16000
    duration = 1.0  # 1 second
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit integers
    audio_data = (audio_data * 32767).astype(np.int16)
    
    return audio_data.tobytes()


@pytest.fixture
def mock_openai_response():
    """Create mock OpenAI API response."""
    return {
        "text": "This is a test transcription.",
        "segments": [
            {
                "start": 0.0,
                "end": 2.5,
                "text": "This is a test transcription."
            }
        ]
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    test_env = {
        "OPENAI_API_KEY": "test-key-123",
        "LOG_LEVEL": "DEBUG",
        "DEBUG": "True",
        "TEMP_DIR": "./test_temp"
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return Mock()


# Pytest markers for different test categories
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]
