#!/usr/bin/env python3
"""
V2T - Voice to Text Desktop Application
Main Entry Point

This is a basic runnable version showing the foundation setup.
Full functionality will be implemented in subsequent phases.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import our foundation components
from utils.logging_config import setup_logging, get_logger
from utils.config import get_config
from utils.constants import APP_NAME, APP_VERSION, StatusMessages
from utils.exceptions import V2TException, ConfigurationError

def main():
    """Main application entry point."""
    try:
        # Set up logging
        logger = setup_logging(log_level="INFO")
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        
        # Load configuration
        logger.info("Loading configuration...")
        config = get_config()
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Debug mode: {config.app.debug}")
        logger.info(f"Log level: {config.app.log_level}")
        
        # Display current status
        print(f"\n🎤 {APP_NAME} v{APP_VERSION}")
        print("=" * 40)
        print(f"Status: {StatusMessages.READY}")
        print(f"Debug Mode: {config.app.debug}")
        print(f"Log Level: {config.app.log_level}")
        print(f"Temp Directory: {config.app.temp_dir}")
        print(f"Window Size: {config.app.window_size}")
        
        # Show API configuration (without exposing the key)
        api_key_status = "✅ Configured" if config.api.openai_api_key else "❌ Missing"
        print(f"OpenAI API Key: {api_key_status}")
        print(f"Whisper Model: {config.api.whisper_model}")
        print(f"GPT Model: {config.api.gpt_model}")
        
        # Show audio configuration
        print(f"\n🔊 Audio Configuration:")
        print(f"Sample Rate: {config.audio.sample_rate} Hz")
        print(f"Channels: {config.audio.channels}")
        print(f"Chunk Size: {config.audio.chunk_size}")
        print(f"Format: {config.audio.format}")
        print(f"Max Duration: {config.audio.max_duration}s")
        
        # Show development phase status
        print(f"\n📋 Development Status:")
        print("✅ Phase 1: Foundation Setup - COMPLETED")
        print("🔄 Phase 2: Audio Processing - IN PROGRESS")
        print("⏳ Phase 3: API Integration - PENDING")
        print("⏳ Phase 4: GUI Implementation - PENDING")
        print("⏳ Phase 5: Application Integration - PENDING")
        
        print(f"\n💡 Next Steps:")
        print("1. Implement audio capture functionality")
        print("2. Add OpenAI API integration")
        print("3. Create GUI interface")
        print("4. Integrate all components")
        
        # Show available commands (for future implementation)
        print(f"\n🎯 Available Commands (Future):")
        print("- Start/Stop Recording")
        print("- Transcribe Audio")
        print("- Clean Text with GPT")
        print("- Save/Load Files")
        
        # Create temp directory if it doesn't exist
        from utils.config import config_manager
        temp_dir = config_manager.create_temp_dir()
        logger.info(f"Temp directory ready: {temp_dir}")
        
        print(f"\n✅ Foundation setup verified successfully!")
        print("The application foundation is ready for Phase 2 development.")
        
        logger.info("Application foundation check completed successfully")
        
    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
        logger.error(f"Configuration error: {e}")
        return 1
        
    except V2TException as e:
        print(f"❌ Application Error: {e}")
        logger.error(f"Application error: {e}")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
