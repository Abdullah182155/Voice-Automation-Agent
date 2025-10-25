"""
Validation module for Voice Automation Agent.
Provides comprehensive validation for dates, times, and user inputs.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import os

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class DateValidator:
    """Validates and processes date-related inputs."""
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Validate if date string is in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_future_date(date_str: str) -> bool:
        """Check if date is in the future."""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.date() >= datetime.now().date()
        except ValueError:
            return False
    
    @staticmethod
    def parse_relative_date(relative_date: str) -> Optional[str]:
        """Parse relative date expressions like 'today', 'tomorrow', etc."""
        now = datetime.now()
        relative_date = relative_date.lower().strip()
        
        if relative_date == "today":
            return now.strftime("%Y-%m-%d")
        elif relative_date == "tomorrow":
            return (now + timedelta(days=1)).strftime("%Y-%m-%d")
        elif relative_date == "next week":
            return (now + timedelta(days=7)).strftime("%Y-%m-%d")
        elif relative_date == "next month":
            return (now + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Handle "next [day of week]"
        days_of_week = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for day_name, day_num in days_of_week.items():
            if f"next {day_name}" in relative_date:
                days_ahead = day_num - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        return None

class TimeValidator:
    """Validates and processes time-related inputs."""
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Validate if time string is in HH:MM format."""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def parse_time_expression(time_str: str) -> Optional[str]:
        """Parse time expressions like '2 PM', 'morning', 'afternoon'."""
        time_str = time_str.lower().strip()
        
        # Handle AM/PM format
        am_pm_match = re.search(r'(\d{1,2})\s*(am|pm)', time_str)
        if am_pm_match:
            hour = int(am_pm_match.group(1))
            period = am_pm_match.group(2)
            
            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            
            return f"{hour:02d}:00"
        
        # Handle relative times
        if "morning" in time_str:
            return "09:00"
        elif "afternoon" in time_str:
            return "14:00"
        elif "evening" in time_str:
            return "18:00"
        elif "night" in time_str:
            return "20:00"
        
        # Handle 24-hour format
        if re.match(r'^\d{1,2}:\d{2}$', time_str):
            return time_str
        
        return None

class InputValidator:
    """Validates user input and intent data."""
    
    @staticmethod
    def validate_appointment_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate appointment booking data."""
        errors = []
        
        # Check required fields
        if not data.get('intent'):
            errors.append("Intent is required")
        
        if data.get('intent') == 'book_schedule':
            if not data.get('date'):
                errors.append("Date is required for booking")
            elif not DateValidator.validate_date_format(data['date']):
                errors.append("Invalid date format (use YYYY-MM-DD)")
            elif not DateValidator.is_future_date(data['date']):
                errors.append("Date must be in the future")
            
            if not data.get('time'):
                errors.append("Time is required for booking")
            elif not TimeValidator.validate_time_format(data['time']):
                errors.append("Invalid time format (use HH:MM)")
            
            if not data.get('description'):
                errors.append("Description is required for booking")
            elif len(data['description'].strip()) < 3:
                errors.append("Description must be at least 3 characters")
        
        return len(errors) == 0, "; ".join(errors)
    
    @staticmethod
    def validate_cancel_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate appointment cancellation data."""
        errors = []
        
        if not data.get('id') and not data.get('description'):
            errors.append("Either appointment ID or description is required for cancellation")
        
        if data.get('id') and not isinstance(data['id'], int):
            errors.append("Appointment ID must be a number")
        
        return len(errors) == 0, "; ".join(errors)
    
    @staticmethod
    def sanitize_description(description: str) -> str:
        """Sanitize and clean description text."""
        if not description:
            return ""
        
        # Remove extra whitespace
        description = re.sub(r'\s+', ' ', description.strip())
        
        # Remove potentially harmful characters
        description = re.sub(r'[<>"\']', '', description)
        
        # Limit length
        if len(description) > 200:
            description = description[:197] + "..."
        
        return description

class LLMResponseValidator:
    """Validates LLM responses and intent data."""
    
    @staticmethod
    def validate_llm_response(response: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate LLM response structure."""
        if not isinstance(response, dict):
            return False, "Response must be a dictionary"
        
        required_fields = ['intent']
        for field in required_fields:
            if field not in response:
                return False, f"Missing required field: {field}"
        
        valid_intents = ['book_schedule', 'cancel_schedule', 'get_schedule', 'unknown']
        if response.get('intent') not in valid_intents:
            return False, f"Invalid intent: {response.get('intent')}"
        
        return True, ""
    
    @staticmethod
    def process_llm_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Process and clean LLM response."""
        processed = response.copy()
        
        # Clean description
        if processed.get('description'):
            processed['description'] = InputValidator.sanitize_description(processed['description'])
        
        # Validate and process dates
        if processed.get('date'):
            # Try to parse relative dates
            relative_date = DateValidator.parse_relative_date(processed['date'])
            if relative_date:
                processed['date'] = relative_date
            elif not DateValidator.validate_date_format(processed['date']):
                processed['date'] = None
        
        # Validate and process times
        if processed.get('time'):
            parsed_time = TimeValidator.parse_time_expression(processed['time'])
            if parsed_time:
                processed['time'] = parsed_time
            elif not TimeValidator.validate_time_format(processed['time']):
                processed['time'] = None
        
        return processed

def validate_environment() -> Tuple[bool, list]:
    """Validate environment configuration."""
    errors = []
    
    # Check required environment variables
    required_vars = ['OPENROUTER_API_KEY']
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing environment variable: {var}")
    
    # Check file existence
    required_files = [
        'prompts/system_prompt.txt',
        'prompts/user_prompt_template.txt'
    ]
    for file_path in required_files:
        if not os.path.exists(file_path):
            errors.append(f"Missing required file: {file_path}")
    
    return len(errors) == 0, errors





