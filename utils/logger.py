"""
Logging module for Voice Automation Agent.
Provides structured logging for debugging and monitoring.
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any

class VoiceAgentLogger:
    """Custom logger for Voice Automation Agent."""
    
    def __init__(self, name: str = "voice_agent", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Setup file handler
        log_file = f"logs/voice_agent_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_user_input(self, text: str, confidence: Optional[float] = None):
        """Log user voice input."""
        self.logger.info(f"User Input: '{text}'" + 
                        (f" (confidence: {confidence:.2f})" if confidence else ""))
    
    def log_llm_request(self, user_input: str, system_prompt: str):
        """Log LLM request details."""
        self.logger.debug(f"LLM Request - User: '{user_input}'")
        self.logger.debug(f"LLM Request - System Prompt: {system_prompt[:100]}...")
    
    def log_llm_response(self, response: Dict[str, Any], processing_time: float):
        """Log LLM response."""
        self.logger.info(f"LLM Response: {response} (processed in {processing_time:.2f}s)")
    
    def log_appointment_action(self, action: str, appointment_data: Dict[str, Any]):
        """Log appointment-related actions."""
        self.logger.info(f"Appointment {action}: {appointment_data}")
    
    def log_api_call(self, endpoint: str, method: str, data: Dict[str, Any], response: Dict[str, Any]):
        """Log external API calls."""
        self.logger.info(f"API Call - {method} {endpoint}")
        self.logger.debug(f"API Request Data: {data}")
        self.logger.debug(f"API Response: {response}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context."""
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    
    def log_validation_error(self, validation_errors: list, input_data: Dict[str, Any]):
        """Log validation errors."""
        self.logger.warning(f"Validation failed for input {input_data}: {validation_errors}")
    
    def log_audio_processing(self, action: str, duration: Optional[float] = None, 
                            file_path: Optional[str] = None):
        """Log audio processing events."""
        message = f"Audio {action}"
        if duration:
            message += f" (duration: {duration:.2f}s)"
        if file_path:
            message += f" (file: {file_path})"
        self.logger.info(message)
    
    def log_system_event(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Log system events."""
        message = f"System Event: {event}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

# Global logger instance
logger = VoiceAgentLogger()

def get_logger(name: str = "voice_agent") -> VoiceAgentLogger:
    """Get logger instance."""
    return VoiceAgentLogger(name)

def log_function_call(func_name: str, args: tuple, kwargs: dict, result: Any = None, 
                     error: Optional[Exception] = None):
    """Decorator for logging function calls."""
    if error:
        logger.log_error(error, f"Function {func_name}")
    else:
        logger.logger.debug(f"Function {func_name} called with args={args}, kwargs={kwargs}")
        if result is not None:
            logger.logger.debug(f"Function {func_name} returned: {result}")

def log_performance(func_name: str, start_time: float, end_time: float):
    """Log function performance."""
    duration = end_time - start_time
    logger.logger.debug(f"Function {func_name} completed in {duration:.3f}s")



