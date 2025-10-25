"""
Manager classes for Voice Automation Agent.
Provides clean interfaces for different system components.
"""

import time
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from config import Config
from utils.logger import logger
from utils.validation import InputValidator, LLMResponseValidator

class SchedulerManager:
    """Manager for local appointment scheduling."""
    
    def __init__(self):
        self.config = Config()
        self.logger = logger
    
    def add_appointment(self, date: str, time: str, description: str) -> Optional[Dict[str, Any]]:
        """Add a new appointment."""
        try:
            from utils.scheduler import add_appointment
            result = add_appointment(date, time, description)
            if result:
                self.logger.log_appointment_action("created", result)
            return result
        except Exception as e:
            self.logger.log_error(e, "Adding appointment")
            return None
    
    def cancel_appointment(self, appointment_id: Optional[int] = None, 
                          description: Optional[str] = None, 
                          date: Optional[str] = None) -> bool:
        """Cancel an appointment."""
        try:
            from utils.scheduler import cancel_appointment
            result = cancel_appointment(appointment_id, description, date)
            if result:
                self.logger.log_appointment_action("canceled", {
                    "id": appointment_id, "description": description, "date": date
                })
            return result
        except Exception as e:
            self.logger.log_error(e, "Canceling appointment")
            return False
    
    def list_appointments(self, date_filter: Optional[str] = None) -> str:
        """List appointments."""
        try:
            from utils.scheduler import list_appointments
            return list_appointments(date_filter)
        except Exception as e:
            self.logger.log_error(e, "Listing appointments")
            return "I encountered an error retrieving your appointments."
    
    def find_appointments(self, query_date: Optional[str] = None,
                         query_description: Optional[str] = None,
                         fuzzy_match: bool = False) -> List[Dict[str, Any]]:
        """Find appointments."""
        try:
            from utils.scheduler import find_appointments
            return find_appointments(query_date, query_description, fuzzy_match)
        except Exception as e:
            self.logger.log_error(e, "Finding appointments")
            return []

class SpeechManager:
    """Manager for speech input/output."""
    
    def __init__(self):
        self.config = Config()
        self.logger = logger
    
    def listen(self) -> Optional[str]:
        """Listen for user speech input."""
        try:
            from utils.speech_io import listen_to_user
            start_time = time.time()
            result = listen_to_user()
            duration = time.time() - start_time
            
            if result:
                self.logger.log_audio_processing("listening", duration)
                self.logger.log_user_input(result)
            else:
                self.logger.log_audio_processing("listening failed", duration)
            
            return result
        except Exception as e:
            self.logger.log_error(e, "Speech recognition")
            return None
    
    def speak(self, text: str):
        """Speak text to user."""
        try:
            from utils.speech_io import speak_response
            start_time = time.time()
            speak_response(text)
            duration = time.time() - start_time
            
            self.logger.log_audio_processing("speaking", duration)
        except Exception as e:
            self.logger.log_error(e, "Text-to-speech")
            print(f"Agent says: {text}")  # Fallback to text output

class LLMManager:
    """Manager for LLM interactions."""
    
    def __init__(self):
        self.config = Config()
        self.logger = logger
    
    def process_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Process user request through LLM."""
        try:
            from utils.llm_interface import get_llm_response, keyword_fallback_parser
            
            start_time = time.time()
            
            # Try LLM first
            llm_response = get_llm_response(user_input)
            processing_time = time.time() - start_time
            
            if llm_response and llm_response.get("intent") != "unknown":
                self.logger.log_llm_response(llm_response, processing_time)
                return llm_response
            else:
                # Fallback to keyword parsing
                self.logger.log_system_event("LLM failed, using fallback parser")
                fallback_response = keyword_fallback_parser(user_input)
                self.logger.log_llm_response(fallback_response, processing_time)
                return fallback_response
                
        except Exception as e:
            self.logger.log_error(e, "LLM processing")
            return None

class APIManager:
    """Manager for external API interactions."""
    
    def __init__(self):
        self.config = Config()
        self.logger = logger
    
    def book_appointment(self, date: str, time: str, description: str) -> Optional[Dict[str, Any]]:
        """Book appointment with external API."""
        try:
            from utils.api_client import book_with_external_api
            
            result = book_with_external_api(date, time, description)
            self.logger.log_api_call(
                f"{self.config.SCHEDULING_API_URL}/book", 
                "POST", 
                {"date": date, "time": time, "description": description},
                result or {}
            )
            return result
        except Exception as e:
            self.logger.log_error(e, "External API booking")
            return None
    
    def cancel_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Cancel appointment with external API."""
        try:
            from utils.api_client import cancel_with_external_api
            
            result = cancel_with_external_api(appointment_id)
            self.logger.log_api_call(
                f"{self.config.SCHEDULING_API_URL}/{appointment_id}", 
                "DELETE", 
                {"id": appointment_id},
                result or {}
            )
            return result
        except Exception as e:
            self.logger.log_error(e, "External API cancellation")
            return None
    
    def get_appointments(self, date_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get appointments from external API."""
        try:
            from utils.api_client import get_external_appointments
            
            result = get_external_appointments(date_filter)
            self.logger.log_api_call(
                f"{self.config.SCHEDULING_API_URL}", 
                "GET", 
                {"date_filter": date_filter},
                result or {}
            )
            return result
        except Exception as e:
            self.logger.log_error(e, "External API retrieval")
            return None

class CalendarManager:
    """Manager for calendar integration."""
    
    def __init__(self):
        self.config = Config()
        self.logger = logger
    
    def add_event(self, appointment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add appointment to calendar."""
        try:
            from utils.calendar_integration import add_to_calendar
            
            result = add_to_calendar(appointment_data)
            if result:
                self.logger.log_appointment_action("added to calendar", result)
            return result
        except Exception as e:
            self.logger.log_error(e, "Calendar integration")
            return None
    
    def remove_event(self, appointment_id: str) -> bool:
        """Remove appointment from calendar."""
        try:
            from utils.calendar_integration import remove_from_calendar
            
            result = remove_from_calendar(appointment_id)
            if result:
                self.logger.log_appointment_action("removed from calendar", {"id": appointment_id})
            return result
        except Exception as e:
            self.logger.log_error(e, "Calendar removal")
            return False
    
    def get_events(self, date_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get calendar events."""
        try:
            from utils.calendar_integration import get_calendar_events
            
            return get_calendar_events(date_filter)
        except Exception as e:
            self.logger.log_error(e, "Calendar retrieval")
            return []
    
    def sync_calendar(self) -> bool:
        """Sync with external calendar systems."""
        try:
            from utils.calendar_integration import sync_calendar
            
            result = sync_calendar()
            if result:
                self.logger.log_system_event("Calendar sync completed")
            return result
        except Exception as e:
            self.logger.log_error(e, "Calendar sync")
            return False
    
    def export_calendar(self) -> Optional[str]:
        """Export calendar to ICS format."""
        try:
            from utils.calendar_integration import export_calendar
            
            result = export_calendar()
            if result:
                self.logger.log_system_event(f"Calendar exported to {result}")
            return result
        except Exception as e:
            self.logger.log_error(e, "Calendar export")
            return None



