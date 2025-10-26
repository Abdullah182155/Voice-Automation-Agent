"""
Data Integration Manager
Synchronizes data between API appointments, calendar events, and local schedules.
Provides unified data management across all three systems.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class UnifiedAppointment:
    """Unified appointment data structure."""
    id: str
    date: str
    time: str
    description: str
    patient_name: Optional[str] = None
    contact_info: Optional[str] = None
    status: str = "confirmed"
    source: str = "local"  # local, api, calendar
    external_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class DataIntegrationManager:
    """
    Manages data synchronization between:
    1. Local schedules (data/schedules.json)
    2. Calendar events (data/calendar_events.json) 
    3. API appointments (data/api_appointments.json)
    """
    
    def __init__(self):
        self.schedules_file = "data/schedules.json"
        self.calendar_file = "data/calendar_events.json"
        self.api_file = "data/api_appointments.json"
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensure all data files exist."""
        os.makedirs("data", exist_ok=True)
        
        for file_path in [self.schedules_file, self.calendar_file, self.api_file]:
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def _load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, file_path: str, data: List[Dict[str, Any]]):
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _convert_to_unified(self, appointment: Dict[str, Any], source: str) -> UnifiedAppointment:
        """Convert appointment data to unified format."""
        # Handle different data structures from different sources
        if source == "schedules":
            return UnifiedAppointment(
                id=str(appointment.get("id", "")),
                date=appointment.get("date", ""),
                time=appointment.get("time", ""),
                description=appointment.get("description", ""),
                source="local",
                created_at=appointment.get("timestamp", "")
            )
        elif source == "calendar":
            # Extract date and time from ISO format
            start_time = appointment.get("start", "")
            if start_time:
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                date = dt.strftime("%Y-%m-%d")
                time = dt.strftime("%H:%M")
            else:
                date = time = ""
            
            return UnifiedAppointment(
                id=str(appointment.get("id", "")),
                date=date,
                time=time,
                description=appointment.get("description", appointment.get("title", "")),
                source="calendar",
                created_at=appointment.get("created_at", "")
            )
        elif source == "api":
            return UnifiedAppointment(
                id=appointment.get("id", ""),
                date=appointment.get("date", ""),
                time=appointment.get("time", ""),
                description=appointment.get("description", ""),
                patient_name=appointment.get("patient_name"),
                contact_info=appointment.get("contact_info"),
                status=appointment.get("status", "confirmed"),
                source="api",
                external_id=appointment.get("appointment_id"),
                created_at=appointment.get("booking_timestamp", "")
            )
        else:
            raise ValueError(f"Unknown source: {source}")
    
    def _convert_from_unified(self, unified_appointment: UnifiedAppointment, target_format: str) -> Dict[str, Any]:
        """Convert unified appointment to target format."""
        if target_format == "schedules":
            return {
                "id": int(unified_appointment.id) if unified_appointment.id.isdigit() else 1,
                "date": unified_appointment.date,
                "time": unified_appointment.time,
                "description": unified_appointment.description,
                "timestamp": unified_appointment.created_at or datetime.now().isoformat()
            }
        elif target_format == "calendar":
            start_datetime = f"{unified_appointment.date}T{unified_appointment.time}:00"
            end_datetime = self._calculate_end_time(unified_appointment.date, unified_appointment.time)
            
            return {
                "id": int(unified_appointment.id) if unified_appointment.id.isdigit() else 1,
                "title": unified_appointment.description,
                "start": start_datetime,
                "end": end_datetime,
                "description": unified_appointment.description,
                "status": unified_appointment.status,
                "created_at": unified_appointment.created_at or datetime.now().isoformat(),
                "calendar_type": "voice_automation"
            }
        elif target_format == "api":
            return {
                "id": unified_appointment.id,
                "date": unified_appointment.date,
                "time": unified_appointment.time,
                "description": unified_appointment.description,
                "patient_name": unified_appointment.patient_name or "Voice User",
                "contact_info": unified_appointment.contact_info or "voice@example.com",
                "status": unified_appointment.status,
                "booking_timestamp": unified_appointment.created_at or datetime.now().isoformat(),
                "confirmation_code": f"CONF_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        else:
            raise ValueError(f"Unknown target format: {target_format}")
    
    def _calculate_end_time(self, date: str, start_time: str, duration_minutes: int = 60) -> str:
        """Calculate end time for appointment."""
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        return end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    
    def get_all_appointments(self) -> List[UnifiedAppointment]:
        """Get all appointments from all sources in unified format."""
        all_appointments = []
        
        # Load from all sources
        schedules = self._load_data(self.schedules_file)
        calendar_events = self._load_data(self.calendar_file)
        api_appointments = self._load_data(self.api_file)
        
        # Convert to unified format
        for appt in schedules:
            try:
                unified = self._convert_to_unified(appt, "schedules")
                all_appointments.append(unified)
            except Exception as e:
                print(f"Error converting schedule appointment: {e}")
        
        for appt in calendar_events:
            try:
                unified = self._convert_to_unified(appt, "calendar")
                all_appointments.append(unified)
            except Exception as e:
                print(f"Error converting calendar event: {e}")
        
        for appt in api_appointments:
            try:
                unified = self._convert_to_unified(appt, "api")
                all_appointments.append(unified)
            except Exception as e:
                print(f"Error converting API appointment: {e}")
        
        return all_appointments
    
    def add_appointment_to_all_systems(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add appointment to all three systems."""
        # Generate unique ID
        appointment_id = f"UNIFIED_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        appointment_data["id"] = appointment_id
        
        results = {}
        
        # Add to schedules
        try:
            schedules = self._load_data(self.schedules_file)
            schedule_appt = self._convert_from_unified(
                self._convert_to_unified(appointment_data, "api"), "schedules"
            )
            schedules.append(schedule_appt)
            self._save_data(self.schedules_file, schedules)
            results["schedules"] = "success"
        except Exception as e:
            results["schedules"] = f"error: {e}"
        
        # Add to calendar
        try:
            calendar_events = self._load_data(self.calendar_file)
            calendar_appt = self._convert_from_unified(
                self._convert_to_unified(appointment_data, "api"), "calendar"
            )
            calendar_events.append(calendar_appt)
            self._save_data(self.calendar_file, calendar_events)
            results["calendar"] = "success"
        except Exception as e:
            results["calendar"] = f"error: {e}"
        
        # Add to API appointments
        try:
            api_appointments = self._load_data(self.api_file)
            api_appointments.append(appointment_data)
            self._save_data(self.api_file, api_appointments)
            results["api"] = "success"
        except Exception as e:
            results["api"] = f"error: {e}"
        
        return results
    
    def remove_appointment_from_all_systems(self, appointment_id: str) -> Dict[str, Any]:
        """Remove appointment from all systems."""
        results = {}
        
        # Remove from schedules
        try:
            schedules = self._load_data(self.schedules_file)
            original_count = len(schedules)
            schedules = [appt for appt in schedules if str(appt.get("id", "")) != appointment_id]
            if len(schedules) < original_count:
                self._save_data(self.schedules_file, schedules)
                results["schedules"] = "removed"
            else:
                results["schedules"] = "not_found"
        except Exception as e:
            results["schedules"] = f"error: {e}"
        
        # Remove from calendar
        try:
            calendar_events = self._load_data(self.calendar_file)
            original_count = len(calendar_events)
            calendar_events = [appt for appt in calendar_events if str(appt.get("id", "")) != appointment_id]
            if len(calendar_events) < original_count:
                self._save_data(self.calendar_file, calendar_events)
                results["calendar"] = "removed"
            else:
                results["calendar"] = "not_found"
        except Exception as e:
            results["calendar"] = f"error: {e}"
        
        # Remove from API appointments
        try:
            api_appointments = self._load_data(self.api_file)
            original_count = len(api_appointments)
            api_appointments = [appt for appt in api_appointments if appt.get("id", "") != appointment_id]
            if len(api_appointments) < original_count:
                self._save_data(self.api_file, api_appointments)
                results["api"] = "removed"
            else:
                results["api"] = "not_found"
        except Exception as e:
            results["api"] = f"error: {e}"
        
        return results
    
    def sync_all_systems(self) -> Dict[str, Any]:
        """Synchronize all systems to ensure consistency."""
        print("Starting full system synchronization...")
        
        # Get all appointments from all sources
        all_appointments = self.get_all_appointments()
        
        # Group by unique identifier (date + time + description)
        unique_appointments = {}
        for appt in all_appointments:
            key = f"{appt.date}_{appt.time}_{appt.description}"
            if key not in unique_appointments:
                unique_appointments[key] = []
            unique_appointments[key].append(appt)
        
        sync_results = {
            "total_unique_appointments": len(unique_appointments),
            "conflicts": [],
            "sync_status": "completed"
        }
        
        # Check for conflicts (same time slot with different details)
        for key, appointments in unique_appointments.items():
            if len(appointments) > 1:
                sync_results["conflicts"].append({
                    "key": key,
                    "appointments": [appt.__dict__ for appt in appointments]
                })
        
        print(f"Synchronization complete. Found {len(sync_results['conflicts'])} conflicts.")
        return sync_results
    
    def get_unified_appointments_summary(self) -> str:
        """Get a unified summary of all appointments."""
        appointments = self.get_all_appointments()
        
        if not appointments:
            return "No appointments found across all systems."
        
        # Sort by date and time
        appointments.sort(key=lambda x: f"{x.date} {x.time}")
        
        summary = f"Found {len(appointments)} appointments across all systems:\n\n"
        
        for appt in appointments:
            summary += f"- {appt.description} on {appt.date} at {appt.time} (Source: {appt.source})\n"
        
        return summary
    
    def export_all_data(self) -> Dict[str, Any]:
        """Export all data from all systems."""
        return {
            "schedules": self._load_data(self.schedules_file),
            "calendar_events": self._load_data(self.calendar_file),
            "api_appointments": self._load_data(self.api_file),
            "unified_appointments": [appt.__dict__ for appt in self.get_all_appointments()],
            "export_timestamp": datetime.now().isoformat()
        }

# Global integration manager instance
integration_manager = DataIntegrationManager()

def sync_all_appointment_systems():
    """Sync all appointment systems."""
    return integration_manager.sync_all_systems()

def get_unified_appointments():
    """Get all appointments in unified format."""
    return integration_manager.get_all_appointments()

def add_appointment_to_all_systems(appointment_data: Dict[str, Any]):
    """Add appointment to all systems."""
    return integration_manager.add_appointment_to_all_systems(appointment_data)

def remove_appointment_from_all_systems(appointment_id: str):
    """Remove appointment from all systems."""
    return integration_manager.remove_appointment_from_all_systems(appointment_id)

def get_appointments_summary():
    """Get unified appointments summary."""
    return integration_manager.get_unified_appointments_summary()

if __name__ == "__main__":
    # Test the integration manager
    print("Testing Data Integration Manager...")
    
    # Test adding appointment
    test_appointment = {
        "date": "2024-12-20",
        "time": "15:00",
        "description": "Integration Test Appointment",
        "patient_name": "Test User",
        "contact_info": "test@example.com"
    }
    
    print("\nAdding appointment to all systems...")
    results = add_appointment_to_all_systems(test_appointment)
    print(f"Results: {json.dumps(results, indent=2)}")
    
    # Test getting unified appointments
    print("\nGetting unified appointments...")
    appointments = get_unified_appointments()
    print(f"Found {len(appointments)} appointments")
    
    # Test summary
    print("\nAppointments summary:")
    print(get_appointments_summary())
    
    # Test sync
    print("\nSynchronizing systems...")
    sync_results = sync_all_systems()
    print(f"Sync results: {json.dumps(sync_results, indent=2)}")
    
    # Test export
    print("\nExporting all data...")
    export_data = integration_manager.export_all_data()
    print(f"Export contains {len(export_data['unified_appointments'])} unified appointments")
