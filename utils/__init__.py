"""
Utils package for Voice Automation Agent.
Provides easy access to all utility modules and classes.
"""

# Import main classes from managers
from .managers import (
    SchedulerManager,
    SpeechManager, 
    LLMManager,
    APIManager,
    CalendarManager
)

# Import validation classes
from .validation import (
    ValidationError,
    DateValidator,
    TimeValidator,
    InputValidator,
    LLMResponseValidator,
    validate_environment
)

# Import core functions
from .scheduler import (
    add_appointment,
    cancel_appointment,
    list_appointments,
    find_appointments
)

from .speech_io import (
    listen_to_user,
    speak_response
)

from .llm_interface import (
    get_llm_response,
    keyword_fallback_parser
)

from .api_client import (
    SchedulingAPIClient,
    book_with_external_api,
    cancel_with_external_api
)

from .calendar_integration import (
    add_to_calendar,
    remove_from_calendar,
    get_calendar_events
)

from .logger import logger

# Make key classes available at package level
__all__ = [
    # Managers
    'SchedulerManager',
    'SpeechManager', 
    'LLMManager',
    'APIManager',
    'CalendarManager',
    
    # Validation
    'ValidationError',
    'DateValidator',
    'TimeValidator',
    'InputValidator',
    'LLMResponseValidator',
    'validate_environment',
    
    # Core functions
    'add_appointment',
    'cancel_appointment', 
    'list_appointments',
    'find_appointments',
    'listen_to_user',
    'speak_response',
    'get_llm_response',
    'keyword_fallback_parser',
    'book_with_external_api',
    'cancel_with_external_api',
    'add_to_calendar',
    'remove_from_calendar',
    'get_calendar_events',
    'logger'
]
