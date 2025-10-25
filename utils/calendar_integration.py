import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class CalendarIntegration:
    """
    Calendar integration for managing appointments across different calendar systems.
    This provides a unified interface for calendar operations.
    """
    
    def __init__(self):
        self.calendar_file = "data/calendar_events.json"
        self._ensure_calendar_file()
    
    def _ensure_calendar_file(self):
        """Ensure the calendar events file exists."""
        if not os.path.exists(self.calendar_file):
            with open(self.calendar_file, 'w') as f:
                json.dump([], f)
    
    def _load_events(self):
        """Load calendar events from file."""
        try:
            with open(self.calendar_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_events(self, events):
        """Save calendar events to file."""
        with open(self.calendar_file, 'w') as f:
            json.dump(events, f, indent=2)
    
    def add_calendar_event(self, appointment_data):
        """
        Add an appointment to the calendar system.
        """
        events = self._load_events()
        
        # Create calendar event
        event = {
            "id": appointment_data.get("id"),
            "title": appointment_data.get("description"),
            "start": f"{appointment_data.get('date')}T{appointment_data.get('time')}:00",
            "end": self._calculate_end_time(appointment_data.get('date'), appointment_data.get('time')),
            "description": appointment_data.get("description"),
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "calendar_type": "voice_automation"
        }
        
        events.append(event)
        self._save_events(events)
        
        return event
    
    def _calculate_end_time(self, date, start_time, duration_minutes=60):
        """
        Calculate end time for an appointment (default 60 minutes).
        """
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        return end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    
    def remove_calendar_event(self, appointment_id):
        """
        Remove an appointment from the calendar system.
        """
        events = self._load_events()
        original_count = len(events)
        
        events = [event for event in events if event.get("id") != appointment_id]
        
        if len(events) < original_count:
            self._save_events(events)
            return True
        return False
    
    def get_calendar_events(self, date_filter=None):
        """
        Get calendar events, optionally filtered by date.
        """
        events = self._load_events()
        
        if date_filter:
            now = datetime.now()
            filtered_events = []
            
            for event in events:
                event_date = datetime.fromisoformat(event["start"]).date()
                
                if date_filter == "today" and event_date == now.date():
                    filtered_events.append(event)
                elif date_filter == "tomorrow" and event_date == (now + timedelta(days=1)).date():
                    filtered_events.append(event)
                elif date_filter == "week":
                    week_end = now + timedelta(days=7)
                    if now.date() <= event_date <= week_end.date():
                        filtered_events.append(event)
                elif date_filter == "month" and event_date.month == now.month and event_date.year == now.year:
                    filtered_events.append(event)
            
            return filtered_events
        
        return events
    
    def sync_with_external_calendar(self, events):
        """
        Sync events with external calendar systems (Google Calendar, Outlook, etc.).
        This is a placeholder for actual calendar API integration.
        """
        print("Syncing with external calendar systems...")
        
        for event in events:
            # In a real implementation, this would integrate with:
            # - Google Calendar API
            # - Microsoft Outlook API
            # - Apple Calendar API
            # - Other calendar services
            
            print(f"Syncing event: {event['title']} on {event['start']}")
        
        return True
    
    def export_calendar_ics(self, filename="appointments.ics"):
        """
        Export calendar events to ICS format for import into other calendar applications.
        """
        events = self._load_events()
        
        ics_content = "BEGIN:VCALENDAR\n"
        ics_content += "VERSION:2.0\n"
        ics_content += "PRODID:-//Voice Automation Agent//Calendar//EN\n"
        
        for event in events:
            ics_content += "BEGIN:VEVENT\n"
            ics_content += f"UID:{event['id']}@voice-automation.local\n"
            ics_content += f"DTSTART:{event['start'].replace('-', '').replace(':', '').replace('T', 'T')}\n"
            ics_content += f"DTEND:{event['end'].replace('-', '').replace(':', '').replace('T', 'T')}\n"
            ics_content += f"SUMMARY:{event['title']}\n"
            ics_content += f"DESCRIPTION:{event['description']}\n"
            ics_content += "STATUS:CONFIRMED\n"
            ics_content += "END:VEVENT\n"
        
        ics_content += "END:VCALENDAR\n"
        
        with open(filename, 'w') as f:
            f.write(ics_content)
        
        return filename

# Global calendar integration instance
calendar = CalendarIntegration()

def add_to_calendar(appointment_data):
    """Add appointment to calendar system."""
    return calendar.add_calendar_event(appointment_data)

def remove_from_calendar(appointment_id):
    """Remove appointment from calendar system."""
    return calendar.remove_calendar_event(appointment_id)

def get_calendar_events(date_filter=None):
    """Get calendar events."""
    return calendar.get_calendar_events(date_filter)

def sync_calendar():
    """Sync with external calendar systems."""
    events = calendar.get_calendar_events()
    return calendar.sync_with_external_calendar(events)

def export_calendar():
    """Export calendar to ICS format."""
    return calendar.export_calendar_ics()

if __name__ == "__main__":
    # Test calendar integration
    print("Testing Calendar Integration...")
    
    # Test adding event
    test_appointment = {
        "id": "TEST_001",
        "date": "2024-12-15",
        "time": "10:00",
        "description": "Test appointment"
    }
    
    event = add_to_calendar(test_appointment)
    print(f"Added event: {json.dumps(event, indent=2)}")
    
    # Test getting events
    events = get_calendar_events()
    print(f"Calendar events: {json.dumps(events, indent=2)}")
    
    # Test export
    ics_file = export_calendar()
    print(f"Exported calendar to: {ics_file}")



