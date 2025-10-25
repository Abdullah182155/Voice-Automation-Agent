"""
Configuration module for Voice Automation Agent.
Centralizes all configuration settings and environment variables.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Voice Automation Agent."""
    
    # API Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
    API_URL = os.getenv("api_url")
    
    # Whisper Configuration
    WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
    WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
    
    # External API Configuration
    SCHEDULING_API_URL = os.getenv("SCHEDULING_API_URL", "http://localhost:8000/api/appointments")
    SCHEDULING_API_KEY = os.getenv("SCHEDULING_API_KEY", "demo_key")
    
    # File Paths
    SCHEDULE_FILE = "data/schedules.json"
    CALENDAR_FILE = "data/calendar_events.json"
    SYSTEM_PROMPT_FILE = "prompts/system_prompt.txt"
    USER_PROMPT_FILE = "prompts/user_prompt_template.txt"
    
    # Audio Configuration
    AUDIO_FORMAT = 16  # pyaudio.paInt16
    AUDIO_CHANNELS = 1
    AUDIO_RATE = 16000
    AUDIO_CHUNK = 512
    RECORD_MAX_SECONDS = 20
    SILENCE_THRESHOLD = 100
    SILENCE_CHUNKS_LIMIT = 2 * (AUDIO_RATE // AUDIO_CHUNK)
    
    # LLM Configuration
    MAX_TOKENS = 150
    TEMPERATURE = 0.3
    
    # Validation
    @classmethod
    def validate_config(cls):
        """Validate configuration settings."""
        errors = []
        
        if not cls.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is required")
        
        if not os.path.exists(cls.SYSTEM_PROMPT_FILE):
            errors.append(f"System prompt file not found: {cls.SYSTEM_PROMPT_FILE}")
        
        if not os.path.exists(cls.USER_PROMPT_FILE):
            errors.append(f"User prompt file not found: {cls.USER_PROMPT_FILE}")
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        return errors
    
    @classmethod
    def get_current_datetime(cls):
        """Get current datetime string for LLM context."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def get_date_info(cls):
        """Get comprehensive date information."""
        now = datetime.now()
        return {
            "current_date": now.strftime("%Y-%m-%d"),
            "current_time": now.strftime("%H:%M:%S"),
            "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "today": now.strftime("%Y-%m-%d"),
            "tomorrow": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
            "next_week": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
            "day_of_week": now.strftime("%A")
        }

