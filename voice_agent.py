"""
Voice Automation Agent - Main Application
A clean, structured voice automation agent for appointment management.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

# Import configuration and utilities
from config import Config
from utils import (
    logger, ValidationError, DateValidator, TimeValidator, InputValidator, 
    LLMResponseValidator, validate_environment,
    SchedulerManager, SpeechManager, LLMManager, APIManager, CalendarManager
)
from utils.data_integration import integration_manager

class VoiceAgent:
    """Main Voice Automation Agent class."""
    
    def __init__(self):
        """Initialize the voice agent."""
        self.config = Config()
        self.logger = logger
        
        # Validate configuration
        self._validate_setup()
        
        # Initialize managers
        self.scheduler = SchedulerManager()
        self.speech = SpeechManager()
        self.llm = LLMManager()
        self.api = APIManager()
        self.calendar = CalendarManager()
        
        self.logger.log_system_event("Voice Agent initialized")
    
    def _validate_setup(self):
        """Validate agent setup and configuration."""
        # Validate environment
        is_valid, errors = validate_environment()
        if not is_valid:
            raise ValidationError(f"Configuration validation failed: {errors}")
        
        # Validate config
        config_errors = self.config.validate_config()
        if config_errors:
            raise ValidationError(f"Config validation failed: {config_errors}")
        
        self.logger.log_system_event("Configuration validated successfully")
    
    def start(self):
        """Start the voice agent main loop."""
        self.logger.log_system_event("Starting Voice Agent")
        
        try:
            self.speech.speak("Hello! I am your voice automation agent. How can I help you today?")
            self._main_loop()
        except KeyboardInterrupt:
            self.logger.log_system_event("Agent stopped by user")
            self.speech.speak("Goodbye! Have a great day!")
        except Exception as e:
            self.logger.log_error(e, "Main loop")
            self.speech.speak("I encountered an error. Please try again.")
    
    def _main_loop(self):
        """Main interaction loop."""
        while True:
            try:
                # Listen for user input
                user_speech = self.speech.listen()
                if not user_speech:
                    self.speech.speak("I didn't catch that. Can you please say something?")
                    continue
                
                self.logger.log_user_input(user_speech)
                
                # Confirm understanding
                if not self._confirm_understanding(user_speech):
                    continue
                
                # Process the request
                self._process_request(user_speech)
                
                # Ask if user needs more help
                self.speech.speak("Is there anything else I can help you with?")
                
            except Exception as e:
                self.logger.log_error(e, "Main loop iteration")
                self.speech.speak("I'm sorry, I encountered an error. Please try again.")
    
    def _confirm_understanding(self, user_speech: str) -> bool:
        """Confirm understanding of user input."""
        self.speech.speak(f"I heard you say: '{user_speech}'. Is that correct?")
        
        while True:
            confirmation = self.speech.listen()
            if confirmation:
                confirmation = confirmation.lower()
                if any(word in confirmation for word in ["yes", "yep", "correct", "right"]):
                    return True
                elif any(word in confirmation for word in ["no", "nope", "wrong", "incorrect"]):
                    self.speech.speak("No problem, please tell me again.")
                    return False
                else:
                    self.speech.speak("I didn't quite catch that. Please say 'yes' or 'no'.")
            else:
                self.speech.speak("I'm having trouble understanding. Please say 'yes' or 'no'.")
    
    def _process_request(self, user_speech: str):
        """Process user request using LLM and execute appropriate action."""
        try:
            # Get LLM response
            llm_response = self.llm.process_request(user_speech)
            if not llm_response:
                self.speech.speak("I'm having trouble understanding. Let me try a different approach.")
                return
            
            self.logger.log_llm_response(llm_response, 0.0)  # TODO: Add timing
            
            # Validate LLM response
            is_valid, error_msg = LLMResponseValidator.validate_llm_response(llm_response)
            if not is_valid:
                self.logger.log_validation_error([error_msg], llm_response)
                self.speech.speak("I had trouble understanding your request. Please try again.")
                return
            
            # Process the intent
            intent = llm_response.get('intent')
            
            if intent == 'book_schedule':
                self._handle_book_appointment(llm_response)
            elif intent == 'cancel_schedule':
                self._handle_cancel_appointment(llm_response)
            elif intent == 'get_schedule':
                self._handle_list_appointments(llm_response)
            elif intent == 'unknown':
                self.speech.speak("I'm not sure how to handle that request. Can you please rephrase or ask about booking, canceling, or listing appointments?")
            else:
                self.speech.speak("I couldn't determine your intent. Please try again.")
                
        except Exception as e:
            self.logger.log_error(e, "Request processing")
            self.speech.speak("I encountered an error processing your request. Please try again.")
    
    def _handle_book_appointment(self, intent_data: Dict[str, Any]):
        """Handle appointment booking."""
        self.speech.speak("You want to book an appointment.")
        
        # Gather missing details
        date = self._get_required_detail("date", intent_data.get('date'))
        time = self._get_required_detail("time", intent_data.get('time'))
        description = self._get_required_detail("description", intent_data.get('description'))
        
        if not all([date, time, description]):
            self.speech.speak("I need a date, time, and description to book an appointment. Please try again with more details.")
            return
        
        # Validate appointment data
        appointment_data = {
            'intent': 'book_schedule',
            'date': date,
            'time': time,
            'description': description
        }
        
        is_valid, error_msg = InputValidator.validate_appointment_data(appointment_data)
        if not is_valid:
            self.speech.speak(f"I found an issue with the appointment details: {error_msg}")
            return
        
        try:
            # Book locally
            new_appointment = self.scheduler.add_appointment(date, time, description)
            if new_appointment:
                self.speech.speak(f"Appointment ID {new_appointment['id']}: '{new_appointment['description']}' on {new_appointment['date']} at {new_appointment['time']} has been booked locally.")
                
                # Add to calendar
                calendar_event = self.calendar.add_event(new_appointment)
                if calendar_event:
                    self.speech.speak("The appointment has also been added to your calendar.")
                
                # Book with external API
                self.speech.speak("Now booking with the external scheduling service...")
                external_result = self.api.book_appointment(date, time, description)
                if external_result and external_result.get("success"):
                    self.speech.speak(f"Great! Your appointment has been confirmed with the external service. Confirmation code: {external_result.get('confirmation_code')}")
                else:
                    self.speech.speak("The appointment was saved locally, but there was an issue with the external booking service.")
            else:
                self.speech.speak("I couldn't book the appointment due to invalid details. Please ensure date and time are correct.")
                
        except Exception as e:
            self.logger.log_error(e, "Appointment booking")
            self.speech.speak("I encountered an error booking the appointment. Please try again.")
    
    def _handle_cancel_appointment(self, intent_data: Dict[str, Any]):
        """Handle appointment cancellation."""
        self.speech.speak("You want to cancel an appointment.")
        
        appt_id = intent_data.get('id')
        description = intent_data.get('description')
        
        if appt_id:
            self.speech.speak(f"You want to cancel appointment ID {appt_id}. Are you sure?")
            if self._get_confirmation():
                self._cancel_by_id(appt_id)
            else:
                self.speech.speak("Cancellation aborted.")
        elif description:
            self._cancel_by_description(description)
        else:
            self.speech.speak("I need either an appointment ID or a clear description to cancel an appointment. Please provide more details.")
    
    def _handle_list_appointments(self, intent_data: Dict[str, Any]):
        """Handle appointment listing using integrated data."""
        date_filter = intent_data.get('date_filter')
        
        try:
            # Get unified appointments from all systems
            all_appointments = integration_manager.get_all_appointments()
            
            if not all_appointments:
                self.speech.speak("You have no appointments scheduled across all systems.")
                return
            
            # Filter by date if specified
            if date_filter:
                filtered_appointments = []
                for appt in all_appointments:
                    if date_filter.lower() in appt.date.lower():
                        filtered_appointments.append(appt)
                all_appointments = filtered_appointments
            
            if not all_appointments:
                self.speech.speak(f"You have no appointments for {date_filter}.")
                return
            
            # Sort appointments by date and time
            all_appointments.sort(key=lambda x: f"{x.date} {x.time}")
            
            # Create unified summary
            summary = f"I found {len(all_appointments)} appointments across all your systems:\n\n"
            
            for appt in all_appointments:
                source_info = f" ({appt.source})" if appt.source != "local" else ""
                summary += f"- {appt.description} on {appt.date} at {appt.time}{source_info}\n"
            
            self.speech.speak(summary)
            
            # Also sync systems to ensure consistency
            sync_results = integration_manager.sync_all_systems()
            if sync_results.get("conflicts"):
                self.speech.speak("I found some conflicts in your appointments. Please check the details.")
            
        except Exception as e:
            self.logger.log_error(e, "Listing unified appointments")
            # Fallback to individual system queries
            self.speech.speak("Let me check your appointments from each system individually.")
            
            local_summary = self.scheduler.list_appointments(date_filter=date_filter)
            self.speech.speak(local_summary)
            
            external_appointments = self.api.get_appointments(date_filter)
            if external_appointments and external_appointments.get("success"):
                external_apts = external_appointments.get("appointments", [])
                if external_apts:
                    self.speech.speak("I also found some appointments from the external service:")
                    for apt in external_apts:
                        self.speech.speak(f"External appointment: {apt['description']} on {apt['date']} at {apt['time']}")
            
            calendar_events = self.calendar.get_events(date_filter)
            if calendar_events:
                self.speech.speak("Here are your calendar events:")
                for event in calendar_events:
                    event_date = event['start'][:10]
                    event_time = event['start'][11:16]
                    self.speech.speak(f"Calendar event: {event['title']} on {event_date} at {event_time}")
    
    def _get_required_detail(self, detail_name: str, current_value: Optional[str]) -> Optional[str]:
        """Get required detail from user."""
        if current_value:
            return current_value
        
        self.speech.speak(f"What is the {detail_name} for the appointment?")
        while True:
            user_input = self.speech.listen()
            if user_input:
                self.speech.speak(f"You said: {user_input}. Is that correct?")
                if self._get_confirmation():
                    return user_input
                else:
                    self.speech.speak(f"Please tell me the {detail_name} again.")
            else:
                self.speech.speak(f"I couldn't hear you. Please tell me the {detail_name}.")
    
    def _get_confirmation(self) -> bool:
        """Get yes/no confirmation from user."""
        while True:
            confirmation = self.speech.listen()
            if confirmation:
                confirmation = confirmation.lower()
                if any(word in confirmation for word in ["yes", "yep", "correct", "right"]):
                    return True
                elif any(word in confirmation for word in ["no", "nope", "wrong", "incorrect"]):
                    return False
                else:
                    self.speech.speak("I didn't quite catch that. Please say 'yes' or 'no'.")
            else:
                self.speech.speak("I'm having trouble understanding. Please say 'yes' or 'no'.")
    
    def _cancel_by_id(self, appt_id: int):
        """Cancel appointment by ID."""
        try:
            if self.scheduler.cancel_appointment(appointment_id=appt_id):
                self.speech.speak(f"Appointment ID {appt_id} has been canceled locally.")
                
                # Remove from calendar
                if self.calendar.remove_event(appt_id):
                    self.speech.speak("The appointment has also been removed from your calendar.")
                
                # Cancel with external API
                external_result = self.api.cancel_appointment(appt_id)
                if external_result and external_result.get("success"):
                    self.speech.speak("The appointment has also been canceled with the external service.")
                else:
                    self.speech.speak("The appointment was canceled locally, but there was an issue with the external service.")
            else:
                self.speech.speak(f"I could not find an appointment with ID {appt_id}.")
        except Exception as e:
            self.logger.log_error(e, f"Canceling appointment {appt_id}")
            self.speech.speak("There was an issue canceling the appointment.")
    
    def _cancel_by_description(self, description: str):
        """Cancel appointment by description."""
        try:
            potential_appointments = self.scheduler.find_appointments(
                query_description=description, fuzzy_match=True
            )
            
            if not potential_appointments:
                self.speech.speak(f"I couldn't find any appointment matching '{description}'. Please provide more details or an ID.")
            elif len(potential_appointments) == 1:
                appt = potential_appointments[0]
                self.speech.speak(f"I found one appointment: '{appt['description']}' on {appt['date']} at {appt['time']}. Do you want to cancel this one?")
                if self._get_confirmation():
                    self._cancel_by_id(appt['id'])
                else:
                    self.speech.speak("Cancellation aborted.")
            else:
                # Multiple matches
                summary = "I found multiple appointments matching your request:\n"
                for appt in potential_appointments[:3]:
                    summary += f"- ID {appt['id']}: '{appt['description']}' on {appt['date']} at {appt['time']}.\n"
                self.speech.speak(summary + "Please specify which one by its ID or provide more details.")
        except Exception as e:
            self.logger.log_error(e, f"Canceling appointment by description: {description}")
            self.speech.speak("There was an issue finding the appointment.")

def main():
    """Main entry point."""
    try:
        agent = VoiceAgent()
        agent.start()
    except ValidationError as e:
        print(f"Configuration Error: {e}")
        print("Please check your configuration and try again.")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        print("Please check the logs for more details.")

if __name__ == "__main__":
    main()



