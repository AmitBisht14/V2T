# V2T Project Structure

**Document Version**: 1.0  
**Last Updated**: 2025-07-30  
**Purpose**: Define the organizational structure and file placement guidelines for the V2T desktop application

---

## 1. Root Directory Structure

```
V2T/
├── .windsurf/                 # Windsurf IDE configuration
│   └── rules/                 # Context engineering rules
│       ├── generate.mdc       # Code generation guidelines
│       └── workflow.mdc       # Development workflow rules
├── Docs/                      # Project documentation
│   ├── Project_structure.md   # This document
│   ├── Implementation.md      # Development guidelines
│   ├── UI_UX_doc.md          # Interface specifications
│   └── Bug_tracking.md       # Issue management process
├── src/                       # Source code directory
│   ├── main.py               # Application entry point
│   ├── gui/                  # User interface components
│   ├── audio/                # Audio processing modules
│   ├── api/                  # External API integrations
│   ├── utils/                # Utility functions and helpers
│   └── tests/                # Test files
├── config/                    # Configuration files
│   ├── .env.example          # Environment variables template
│   └── settings.json         # Application settings
├── assets/                    # Static resources
│   ├── icons/                # Application icons
│   └── sounds/               # Audio feedback files
├── build/                     # Build artifacts (generated)
├── dist/                      # Distribution files (generated)
├── requirements.txt           # Python dependencies
├── setup.py                  # Package setup configuration
├── README.md                 # Project overview and setup
├── .gitignore               # Git ignore rules
└── PRD.md                   # Product Requirements Document
```

## 2. Source Code Organization (`src/`)

### 2.1 Main Application (`src/main.py`)
- **Purpose**: Application entry point and initialization
- **Responsibilities**:
  - Initialize logging
  - Load configuration
  - Create main window
  - Handle application lifecycle

### 2.2 GUI Module (`src/gui/`)
```
src/gui/
├── __init__.py
├── main_window.py           # Primary application window
├── widgets/
│   ├── __init__.py
│   ├── audio_controls.py    # Start/Stop recording buttons
│   ├── text_display.py     # Transcript display widget
│   ├── status_bar.py       # Status and progress indicators
│   └── menu_bar.py         # Application menu (if needed)
├── dialogs/
│   ├── __init__.py
│   ├── settings_dialog.py   # Configuration dialog
│   └── error_dialog.py      # Error message dialogs
└── styles/
    ├── __init__.py
    └── themes.py           # UI styling and themes
```

### 2.3 Audio Module (`src/audio/`)
```
src/audio/
├── __init__.py
├── recorder.py              # Audio capture and recording
├── processor.py             # Audio file processing
├── formats.py               # Audio format handling
└── devices.py               # Audio device management
```

### 2.4 API Module (`src/api/`)
```
src/api/
├── __init__.py
├── base_client.py           # Base API client with common functionality
├── whisper_client.py        # OpenAI Whisper API integration
├── gpt_client.py           # OpenAI GPT API integration
├── exceptions.py           # API-specific exceptions
└── models.py               # Data models for API responses
```

### 2.5 Utils Module (`src/utils/`)
```
src/utils/
├── __init__.py
├── config.py               # Configuration management
├── logging_config.py       # Logging setup and configuration
├── file_helpers.py         # File operations utilities
├── validators.py           # Input validation functions
└── constants.py            # Application constants
```

### 2.6 Tests Module (`src/tests/`)
```
src/tests/
├── __init__.py
├── conftest.py             # Pytest configuration and fixtures
├── unit/
│   ├── __init__.py
│   ├── test_audio.py       # Audio module tests
│   ├── test_api.py         # API module tests
│   ├── test_utils.py       # Utils module tests
│   └── test_gui.py         # GUI component tests
├── integration/
│   ├── __init__.py
│   ├── test_audio_api.py   # Audio + API integration tests
│   └── test_full_workflow.py # End-to-end workflow tests
└── fixtures/
    ├── __init__.py
    ├── sample_audio.wav     # Test audio files
    └── mock_responses.json  # Mock API responses
```

## 3. Configuration Structure (`config/`)

### 3.1 Environment Variables (`.env`)
```bash
# API Configuration
OPENAI_API_KEY=your_api_key_here
WHISPER_MODEL=whisper-1
GPT_MODEL=gpt-3.5-turbo

# Audio Settings
SAMPLE_RATE=16000
CHANNELS=1
CHUNK_SIZE=1024

# Application Settings
LOG_LEVEL=INFO
TEMP_DIR=./temp
```

### 3.2 Application Settings (`settings.json`)
```json
{
  "audio": {
    "default_device": null,
    "sample_rate": 16000,
    "channels": 1,
    "format": "wav"
  },
  "ui": {
    "theme": "default",
    "window_size": [800, 600],
    "remember_position": true
  },
  "processing": {
    "cleanup_temp_files": true,
    "max_recording_duration": 300,
    "auto_cleanup_enabled": true
  }
}
```

## 4. File Naming Conventions

### 4.1 Python Files
- **Modules**: `snake_case.py` (e.g., `audio_recorder.py`)
- **Classes**: `PascalCase` (e.g., `AudioRecorder`)
- **Functions**: `snake_case` (e.g., `start_recording`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RECORDING_TIME`)

### 4.2 Configuration Files
- **Environment**: `.env` (production), `.env.example` (template)
- **Settings**: `settings.json`, `config.yaml`
- **Logs**: `app.log`, `error.log`

### 4.3 Asset Files
- **Icons**: `icon_name.ico`, `icon_name.png`
- **Sounds**: `sound_name.wav`, `sound_name.mp3`
- **Images**: `image_name.png`, `image_name.jpg`

## 5. Directory Creation Guidelines

### 5.1 When to Create New Directories
- **Functional Grouping**: When you have 3+ related files
- **Logical Separation**: Different concerns or responsibilities
- **Scalability**: Anticipating future growth in that area

### 5.2 Directory Naming Rules
- Use `snake_case` for directory names
- Keep names descriptive but concise
- Avoid abbreviations unless widely understood
- Group related functionality together

## 6. Import Structure Guidelines

### 6.1 Import Order (PEP 8)
1. Standard library imports
2. Related third-party imports
3. Local application/library imports

### 6.2 Example Import Structure
```python
# Standard library
import os
import sys
import threading
from typing import Optional, Dict, Any

# Third-party
import tkinter as tk
from tkinter import ttk
import pyaudio
import requests

# Local imports
from src.utils.config import Config
from src.api.whisper_client import WhisperClient
from src.gui.widgets.audio_controls import AudioControls
```

## 7. Build and Distribution Structure

### 7.1 Build Directory (`build/`)
- **Purpose**: Temporary build artifacts
- **Contents**: Compiled files, intermediate build files
- **Git Status**: Ignored (in `.gitignore`)

### 7.2 Distribution Directory (`dist/`)
- **Purpose**: Final executable and distribution files
- **Contents**: `.exe` files, installers, packaged applications
- **Git Status**: Ignored (in `.gitignore`)

## 8. Context Engineering Integration

### 8.1 For Claude Interactions
- Always reference this structure when creating new files
- Place files in appropriate directories based on functionality
- Follow naming conventions consistently
- Maintain the separation of concerns defined here

### 8.2 File Placement Decision Tree
```
New File Needed?
├── GUI Component? → src/gui/
├── Audio Processing? → src/audio/
├── API Integration? → src/api/
├── Utility Function? → src/utils/
├── Test File? → src/tests/
├── Configuration? → config/
├── Documentation? → Docs/
└── Asset/Resource? → assets/
```

## 9. Maintenance Guidelines

### 9.1 Regular Structure Review
- Review structure monthly for optimization opportunities
- Refactor when directories become too large (>10 files)
- Consolidate when directories have too few files (<3 files)

### 9.2 Documentation Updates
- Update this document when structure changes
- Maintain consistency with PRD requirements
- Keep examples current with actual implementation

---

*This document serves as the definitive guide for V2T project organization and should be referenced for all file placement decisions.*