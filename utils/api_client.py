import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SCHEDULING_API_URL = os.getenv("SCHEDULING_API_URL", "http://localhost:8000/api/appointments")
SCHEDULING_API_KEY = os.getenv("SCHEDULING_API_KEY", "demo_key")

class SchedulingAPIClient:
    """
    Client for interacting with external scheduling API endpoints.
    This simulates booking appointments with an external service.
    """
    
    def __init__(self):
        self.base_url = SCHEDULING_API_URL
        self.api_key = SCHEDULING_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def book_appointment(self, date, time, description, patient_name=None, contact_info=None):
        """
        Books an appointment with the external scheduling service.
        Returns appointment details or None if booking fails.
        """
        appointment_data = {
            "date": date,
            "time": time,
            "description": description,
            "patient_name": patient_name or "Voice User",
            "contact_info": contact_info or "voice@example.com",
            "booking_timestamp": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        try:
            # Make real API call to FastAPI server
            response = requests.post(f"{self.base_url}/book", headers=self.headers, json=appointment_data)
            
            print(f"API Call: Booking appointment with external service...")
            print(f"Data: {json.dumps(appointment_data, indent=2)}")
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "message": response.text
                }
            
        except Exception as e:
            print(f"Error booking appointment with external service: {e}")
            return None
    
    def cancel_appointment(self, appointment_id):
        """
        Cancels an appointment with the external scheduling service.
        """
        try:
            # Make real API call to FastAPI server
            response = requests.delete(f"{self.base_url}/{appointment_id}", headers=self.headers)
            
            print(f"API Call: Canceling appointment {appointment_id} with external service...")
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "message": response.text
                }
            
        except Exception as e:
            print(f"Error canceling appointment with external service: {e}")
            return None
    
    def get_appointments(self, date_filter=None):
        """
        Retrieves appointments from the external scheduling service.
        """
        try:
            # Make real API call to FastAPI server
            params = {"date_filter": date_filter} if date_filter else {}
            response = requests.get(f"{self.base_url}", headers=self.headers, params=params)
            
            print(f"API Call: Fetching appointments from external service...")
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "message": response.text
                }
            
        except Exception as e:
            print(f"Error fetching appointments from external service: {e}")
            return None

# Global API client instance
api_client = SchedulingAPIClient()

def book_with_external_api(date, time, description, patient_name=None, contact_info=None):
    """
    Wrapper function to book appointment with external API.
    """
    return api_client.book_appointment(date, time, description, patient_name, contact_info)

def cancel_with_external_api(appointment_id):
    """
    Wrapper function to cancel appointment with external API.
    """
    return api_client.cancel_appointment(appointment_id)

def get_external_appointments(date_filter=None):
    """
    Wrapper function to get appointments from external API.
    """
    return api_client.get_appointments(date_filter)

if __name__ == "__main__":
    # Test the API client
    print("Testing Scheduling API Client...")
    
    # Test booking with a future date
    from datetime import datetime, timedelta
    future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    result = book_with_external_api(future_date, "10:00", "Doctor consultation")
    print(f"Booking result: {json.dumps(result, indent=2)}")
    
    # Test getting appointments
    appointments = get_external_appointments()
    print(f"Appointments: {json.dumps(appointments, indent=2)}")



