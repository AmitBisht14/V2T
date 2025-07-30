# V2T Implementation Guidelines

**Document Version**: 1.0  
**Last Updated**: 2025-07-30  
**Purpose**: Detailed coding standards and development patterns for the V2T desktop application

---

## 1. Development Environment Setup

### 1.1 Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 1.2 Required Dependencies
```txt
# requirements.txt
tkinter>=8.6  # GUI framework (usually built-in)
pyaudio>=0.2.11  # Audio capture
requests>=2.28.0  # HTTP client
openai>=1.0.0  # OpenAI API client
pytest>=7.0.0  # Testing framework
pytest-mock>=3.10.0  # Mocking for tests
pyinstaller>=5.0.0  # Executable packaging
```

### 1.3 IDE Configuration
- **Recommended**: VS Code with Python extension
- **Linting**: Enable flake8 or pylint
- **Formatting**: Use black or autopep8
- **Type Checking**: Enable mypy

## 2. Code Style Standards

### 2.1 Python Style Guide (PEP 8)
```python
# Good: Clear, descriptive names
class AudioRecorder:
    def start_recording(self) -> bool:
        """Start audio recording session."""
        pass

# Bad: Unclear abbreviations
class AR:
    def start_rec(self):
        pass
```

### 2.2 Type Hints
```python
from typing import Optional, Dict, List, Callable

def process_audio(file_path: str, callback: Optional[Callable] = None) -> Dict[str, str]:
    """Process audio file and return transcript data."""
    result: Dict[str, str] = {}
    return result
```

### 2.3 Docstring Standards
```python
def transcribe_audio(audio_file: str, model: str = "whisper-1") -> str:
    """
    Transcribe audio file using OpenAI Whisper API.
    
    Args:
        audio_file: Path to the audio file to transcribe
        model: Whisper model to use for transcription
        
    Returns:
        Transcribed text as string
        
    Raises:
        APIError: If API request fails
        FileNotFoundError: If audio file doesn't exist
    """
    pass
```

## 3. Architecture Patterns

### 3.1 MVC Pattern Implementation
```python
# Model: Data and business logic
class AudioModel:
    def __init__(self):
        self.current_recording = None
        self.transcript = ""
    
    def start_recording(self) -> bool:
        # Business logic here
        pass

# View: GUI components
class MainWindow:
    def __init__(self, controller):
        self.controller = controller
        self.setup_ui()
    
    def on_record_button_click(self):
        self.controller.handle_record_request()

# Controller: Coordination logic
class AppController:
    def __init__(self):
        self.model = AudioModel()
        self.view = MainWindow(self)
    
    def handle_record_request(self):
        success = self.model.start_recording()
        self.view.update_record_status(success)
```

### 3.2 Dependency Injection
```python
class WhisperClient:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com"):
        self.api_key = api_key
        self.base_url = base_url

class AudioProcessor:
    def __init__(self, whisper_client: WhisperClient):
        self.whisper_client = whisper_client  # Injected dependency
    
    def process(self, audio_file: str) -> str:
        return self.whisper_client.transcribe(audio_file)
```

## 4. Error Handling Patterns

### 4.1 Custom Exceptions
```python
class V2TException(Exception):
    """Base exception for V2T application."""
    pass

class AudioError(V2TException):
    """Audio processing related errors."""
    pass

class APIError(V2TException):
    """API communication errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
```

### 4.2 Error Handling Strategy
```python
def safe_api_call(func: Callable) -> Callable:
    """Decorator for safe API calls with retry logic."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise APIError(f"API call failed after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    return wrapper
```

## 5. Threading and Async Patterns

### 5.1 Non-blocking UI Operations
```python
import threading
from tkinter import ttk

class AudioControls:
    def __init__(self):
        self.is_processing = False
        self.progress_bar = ttk.Progressbar()
    
    def process_audio_async(self, audio_file: str):
        """Process audio without blocking UI."""
        if self.is_processing:
            return
        
        def worker():
            try:
                self.is_processing = True
                self.progress_bar.start()
                
                # API processing logic here
                result = self.api_client.process(audio_file)
                
                # Update UI on main thread
                self.root.after(0, self.on_processing_complete, result)
            except Exception as e:
                self.root.after(0, self.on_processing_error, str(e))
            finally:
                self.is_processing = False
                self.progress_bar.stop()
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
```

## 6. Configuration Management

### 6.1 Configuration Class
```python
import os
import json
from typing import Dict, Any

class Config:
    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file and environment."""
        # Load from JSON file
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self._config = json.load(f)
        
        # Override with environment variables
        self._config['openai_api_key'] = os.getenv('OPENAI_API_KEY', '')
        self._config['log_level'] = os.getenv('LOG_LEVEL', 'INFO')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
```

## 7. Logging Standards

### 7.1 Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO"):
    """Configure application logging."""
    logger = logging.getLogger('v2t')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log', maxBytes=10*1024*1024, backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger
```

## 8. Testing Patterns

### 8.1 Unit Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from src.audio.recorder import AudioRecorder

class TestAudioRecorder:
    def setup_method(self):
        """Setup for each test method."""
        self.recorder = AudioRecorder()
    
    def test_start_recording_success(self):
        """Test successful recording start."""
        with patch('pyaudio.PyAudio') as mock_pyaudio:
            mock_stream = Mock()
            mock_pyaudio.return_value.open.return_value = mock_stream
            
            result = self.recorder.start_recording()
            
            assert result is True
            mock_pyaudio.return_value.open.assert_called_once()
    
    def test_start_recording_device_error(self):
        """Test recording start with device error."""
        with patch('pyaudio.PyAudio') as mock_pyaudio:
            mock_pyaudio.return_value.open.side_effect = Exception("Device not found")
            
            with pytest.raises(AudioError):
                self.recorder.start_recording()
```

## 9. Security Best Practices

### 9.1 API Key Management
```python
import os
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self.cipher_suite = None
        self._load_encryption_key()
    
    def _load_encryption_key(self):
        """Load or generate encryption key."""
        key_file = 'config/.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        
        self.cipher_suite = Fernet(key)
    
    def encrypt_api_key(self, api_key: str) -> bytes:
        """Encrypt API key for storage."""
        return self.cipher_suite.encrypt(api_key.encode())
    
    def decrypt_api_key(self, encrypted_key: bytes) -> str:
        """Decrypt API key for use."""
        return self.cipher_suite.decrypt(encrypted_key).decode()
```

## 10. Performance Optimization

### 10.1 Memory Management
```python
import gc
import tempfile
import os

class AudioProcessor:
    def __init__(self):
        self.temp_files = []
    
    def process_audio(self, audio_data: bytes) -> str:
        """Process audio with proper cleanup."""
        temp_file = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                temp_file = f.name
                f.write(audio_data)
                self.temp_files.append(temp_file)
            
            # Process the file
            result = self._transcribe_file(temp_file)
            return result
            
        finally:
            # Cleanup
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
                if temp_file in self.temp_files:
                    self.temp_files.remove(temp_file)
            
            # Force garbage collection for large audio data
            del audio_data
            gc.collect()
```

## 11. Code Review Checklist

### 11.1 Before Committing
- [ ] Code follows PEP 8 standards
- [ ] All functions have type hints
- [ ] Comprehensive docstrings added
- [ ] Error handling implemented
- [ ] Unit tests written and passing
- [ ] No hardcoded secrets or API keys
- [ ] Memory cleanup implemented
- [ ] Threading safety considered
- [ ] Logging added for debugging
- [ ] Configuration externalized

### 11.2 Architecture Review
- [ ] Follows MVC pattern
- [ ] Proper separation of concerns
- [ ] Dependencies injected, not hardcoded
- [ ] Interfaces used for testability
- [ ] Single responsibility principle followed
- [ ] Open/closed principle respected

## 12. Git Strategy and Commit Guidelines

### 12.1 Commit Message Format

#### 12.1.1 Conventional Commits Standard
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### 12.1.2 Commit Types
- **feat**: New feature implementation
- **fix**: Bug fixes
- **docs**: Documentation changes
- **style**: Code formatting (no logic changes)
- **refactor**: Code restructuring (no feature changes)
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, or tooling

#### 12.1.3 Scope Examples
- **audio**: Audio recording/processing functionality
- **api**: OpenAI API integrations
- **gui**: User interface components
- **config**: Configuration management
- **utils**: Utility functions
- **tests**: Test-related changes

#### 12.1.4 Example Commit Messages
```bash
# Good examples
feat(audio): implement start/stop recording functionality
fix(api): handle Whisper API timeout errors
docs(readme): add installation instructions
refactor(gui): extract button components to separate files
test(audio): add unit tests for recorder module

# Bad examples
fix: stuff
update code
working on gui
```

### 12.2 Branch Strategy

#### 12.2.1 Branch Naming Convention
```
<type>/<scope>-<short-description>
```

Examples:
```bash
feature/audio-recording
fix/api-timeout-handling
docs/implementation-guidelines
refactor/gui-components
```

#### 12.2.2 Branch Types
- **feature/**: New feature development
- **fix/**: Bug fixes
- **hotfix/**: Critical production fixes
- **docs/**: Documentation updates
- **refactor/**: Code restructuring
- **experiment/**: Experimental work

#### 12.2.3 Branch Lifecycle
1. **Create**: Branch from `main` for new work
2. **Develop**: Make commits following message conventions
3. **Test**: Ensure all tests pass before merge
4. **Review**: Self-review changes against checklist
5. **Merge**: Merge back to `main` when complete
6. **Cleanup**: Delete feature branch after merge

### 12.3 Development Phase Integration

#### 12.3.1 Phase-Based Commits
Align commits with Task_breakdown.md phases:

```bash
# Phase 1: Foundation Setup
feat(config): implement configuration management system
feat(utils): add custom exception classes
feat(logging): set up rotating file logger

# Phase 2: Audio Processing
feat(audio): implement PyAudio recorder class
feat(audio): add audio device detection
fix(audio): handle microphone permission errors

# Phase 3: API Integration
feat(api): implement Whisper API client
feat(api): add GPT text cleanup integration
fix(api): handle rate limiting with exponential backoff

# Phase 4: GUI Implementation
feat(gui): create main application window
feat(gui): implement START/STOP button controls
feat(gui): add text display widget with editing

# Phase 5: Integration
feat(app): integrate all components in main.py
feat(controller): implement MVC coordination logic
fix(threading): resolve UI blocking during API calls
```

#### 12.3.2 Task Completion Commits
When completing tasks from Task_breakdown.md:
```bash
# Reference specific tasks
feat(audio): implement start_recording() method

Completes task from Phase 2.1:
- [x] Implement start_recording() method
- Includes error handling for device access
- Adds logging for debugging
- Unit tests included

Closes #12
```

### 12.4 Commit Frequency Guidelines

#### 12.4.1 When to Commit
- **Logical Units**: Complete a specific function or fix
- **Working State**: Code compiles and basic functionality works
- **Before Breaks**: Before lunch, end of day, or switching tasks
- **Milestone Completion**: When finishing a task from Task_breakdown.md

#### 12.4.2 Commit Size Guidelines
- **Small Commits**: 1-50 lines changed (preferred)
- **Medium Commits**: 50-200 lines changed (acceptable)
- **Large Commits**: 200+ lines changed (avoid, break down)

#### 12.4.3 What NOT to Commit
- **Broken Code**: Code that doesn't compile or run
- **Debug Code**: Temporary print statements or debug flags
- **Secrets**: API keys, passwords, or sensitive data
- **Generated Files**: Build artifacts, compiled files
- **IDE Files**: Editor-specific configuration files

### 12.5 Pre-Commit Checklist

#### 12.5.1 Code Quality Checks
- [ ] Code follows PEP 8 standards
- [ ] All functions have type hints and docstrings
- [ ] No hardcoded secrets or API keys
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Code is properly formatted

#### 12.5.2 Functional Checks
- [ ] Code runs without errors
- [ ] New functionality works as expected
- [ ] Existing functionality not broken
- [ ] Unit tests pass (if applicable)
- [ ] Integration tests pass (if applicable)

#### 12.5.3 Documentation Checks
- [ ] Code changes documented in docstrings
- [ ] README updated if needed
- [ ] Task_breakdown.md updated with progress
- [ ] Comments added for complex logic

### 12.6 Integration with Development Workflow

#### 12.6.1 Daily Development Pattern
```bash
# Start of day
git pull origin main
git checkout -b feature/new-functionality

# During development
# ... make changes ...
git add .
git commit -m "feat(scope): implement specific functionality"

# ... more changes ...
git commit -m "test(scope): add unit tests for new functionality"

# End of task/day
git push origin feature/new-functionality

# When feature complete
git checkout main
git merge feature/new-functionality
git push origin main
git branch -d feature/new-functionality
```

#### 12.6.2 Phase Completion Strategy
At the end of each development phase:
```bash
# Create phase completion commit
git add .
git commit -m "feat(phase-N): complete Phase N implementation

Phase N: [Phase Name] - COMPLETE
✅ All tasks in phase completed
✅ Unit tests passing
✅ Integration tests successful
✅ Code review completed
✅ Documentation updated

Next: Begin Phase N+1"

# Tag major milestones
git tag -a v0.N.0 -m "Phase N: [Phase Name] Complete"
git push origin v0.N.0
```

### 12.7 Emergency Procedures

#### 12.7.1 Hotfix Process
For critical issues in main branch:
```bash
git checkout main
git checkout -b hotfix/critical-issue-description
# ... make minimal fix ...
git commit -m "hotfix(scope): fix critical issue description"
git checkout main
git merge hotfix/critical-issue-description
git push origin main
git branch -d hotfix/critical-issue-description
```

#### 12.7.2 Rollback Strategy
If a commit breaks functionality:
```bash
# Identify problematic commit
git log --oneline

# Revert specific commit
git revert <commit-hash>
git commit -m "revert: rollback problematic change

This reverts commit <commit-hash> due to:
- [specific issue description]
- [impact on functionality]"
```

---

*This Git strategy ensures consistent, traceable, and professional version control practices aligned with the V2T development phases.*

---

*These implementation guidelines ensure consistent, maintainable, and secure code development for the V2T project.*