"""
FastAPI Server for Appointment Scheduling API
Provides REST endpoints for appointment management that can be tested with Postman.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import os
import uuid
import sys

# Add utils directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from data_integration import integration_manager

# Initialize FastAPI app
app = FastAPI(
    title="Appointment Scheduling API",
    description="API for managing appointments - designed for voice agent integration",
    version="1.0.0"
)

# Add CORS middleware for testing with Postman
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage file
APPOINTMENTS_FILE = "data/api_appointments.json"

# Pydantic models
class AppointmentRequest(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM format")
    description: str = Field(..., description="Appointment description")
    patient_name: Optional[str] = Field(None, description="Patient name")
    contact_info: Optional[str] = Field(None, description="Contact information")

class AppointmentResponse(BaseModel):
    success: bool
    appointment_id: str
    confirmation_code: str
    appointment: Dict[str, Any]
    message: str

class AppointmentListResponse(BaseModel):
    success: bool
    appointments: List[Dict[str, Any]]
    total_count: int

class CancelResponse(BaseModel):
    success: bool
    appointment_id: str
    message: str

# Helper functions
def load_appointments() -> List[Dict[str, Any]]:
    """Load appointments from JSON file."""
    if not os.path.exists(APPOINTMENTS_FILE):
        return []
    
    try:
        with open(APPOINTMENTS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_appointments(appointments: List[Dict[str, Any]]):
    """Save appointments to JSON file."""
    os.makedirs("data", exist_ok=True)
    with open(APPOINTMENTS_FILE, "w") as f:
        json.dump(appointments, f, indent=2)

def generate_appointment_id() -> str:
    """Generate unique appointment ID."""
    return f"EXT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{str(uuid.uuid4())[:8]}"

def generate_confirmation_code() -> str:
    """Generate confirmation code."""
    return f"CONF_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# API Endpoints

@app.get("/", summary="API Health Check")
async def root():
    """Health check endpoint."""
    return {
        "message": "Appointment Scheduling API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/appointments/book", 
          response_model=AppointmentResponse,
          summary="Book New Appointment",
          description="Create a new appointment booking")
async def book_appointment(appointment: AppointmentRequest):
    """Book a new appointment."""
    try:
        # Validate date and time format
        try:
            full_datetime_str = f"{appointment.date} {appointment.time}"
            datetime_obj = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."
            )
        
        # Check if appointment is in the past
        if datetime_obj < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book appointments in the past"
            )
        
        # Check for conflicts using integration manager
        all_appointments = integration_manager.get_all_appointments()
        for existing_appt in all_appointments:
            if (existing_appt.date == appointment.date and 
                existing_appt.time == appointment.time):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Appointment slot {appointment.date} {appointment.time} is already booked"
                )
        
        # Create new appointment data
        appointment_data = {
            "date": appointment.date,
            "time": appointment.time,
            "description": appointment.description,
            "patient_name": appointment.patient_name or "Voice User",
            "contact_info": appointment.contact_info or "voice@example.com",
            "status": "confirmed",
            "booking_timestamp": datetime.now().isoformat()
        }
        
        # Add to all systems using integration manager
        results = integration_manager.add_appointment_to_all_systems(appointment_data)
        
        # Check if any system failed
        failed_systems = [system for system, result in results.items() if "error" in result]
        if failed_systems:
            print(f"Warning: Failed to add to systems: {failed_systems}")
        
        # Get the created appointment
        appointment_id = appointment_data["id"]
        confirmation_code = f"CONF_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return AppointmentResponse(
            success=True,
            appointment_id=appointment_id,
            confirmation_code=confirmation_code,
            appointment=appointment_data,
            message="Appointment successfully booked and synchronized across all systems"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/appointments", 
         response_model=AppointmentListResponse,
         summary="Get All Appointments",
         description="Retrieve all appointments with optional date filtering")
async def get_appointments(date_filter: Optional[str] = None):
    """Get all appointments with optional filtering."""
    try:
        # Get unified appointments from all systems
        all_appointments = integration_manager.get_all_appointments()
        
        # Convert to API format
        appointments = []
        for appt in all_appointments:
            api_appt = {
                "id": appt.id,
                "date": appt.date,
                "time": appt.time,
                "description": appt.description,
                "patient_name": appt.patient_name,
                "contact_info": appt.contact_info,
                "status": appt.status,
                "source": appt.source,
                "created_at": appt.created_at
            }
            appointments.append(api_appt)
        
        # Apply date filter if provided
        if date_filter:
            filtered_appointments = []
            for appt in appointments:
                if date_filter.lower() in appt["date"].lower():
                    filtered_appointments.append(appt)
            appointments = filtered_appointments
        
        return AppointmentListResponse(
            success=True,
            appointments=appointments,
            total_count=len(appointments)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/appointments/{appointment_id}",
         summary="Get Specific Appointment",
         description="Retrieve a specific appointment by ID")
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID."""
    try:
        appointments = load_appointments()
        
        for appt in appointments:
            if appt["id"] == appointment_id:
                return {
                    "success": True,
                    "appointment": appt
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.delete("/api/appointments/{appointment_id}",
            response_model=CancelResponse,
            summary="Cancel Appointment",
            description="Cancel an appointment by ID")
async def cancel_appointment(appointment_id: str):
    """Cancel an appointment by ID."""
    try:
        # Remove from all systems using integration manager
        results = integration_manager.remove_appointment_from_all_systems(appointment_id)
        
        # Check if appointment was found in any system
        removed_systems = [system for system, result in results.items() if result == "removed"]
        
        if removed_systems:
            return CancelResponse(
                success=True,
                appointment_id=appointment_id,
                message=f"Appointment successfully canceled from systems: {', '.join(removed_systems)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Appointment with ID {appointment_id} not found in any system"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/appointments/health", summary="API Health Check")
async def health_check():
    """Detailed health check."""
    all_appointments = integration_manager.get_all_appointments()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_appointments": len(all_appointments),
        "api_version": "1.0.0",
        "integration_status": "active"
    }

@app.post("/api/appointments/sync", summary="Synchronize All Systems")
async def sync_systems():
    """Synchronize all appointment systems."""
    try:
        sync_results = integration_manager.sync_all_systems()
        return {
            "success": True,
            "message": "Systems synchronized successfully",
            "results": sync_results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )

@app.get("/api/appointments/unified", summary="Get Unified Appointments")
async def get_unified_appointments():
    """Get all appointments in unified format from all systems."""
    try:
        appointments = integration_manager.get_all_appointments()
        return {
            "success": True,
            "appointments": [appt.__dict__ for appt in appointments],
            "total_count": len(appointments)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unified appointments: {str(e)}"
        )

@app.get("/api/appointments/summary", summary="Get Appointments Summary")
async def get_appointments_summary():
    """Get unified appointments summary."""
    try:
        summary = integration_manager.get_unified_appointments_summary()
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )

@app.get("/api/appointments/export", summary="Export All Data")
async def export_all_data():
    """Export all data from all systems."""
    try:
        export_data = integration_manager.export_all_data()
        return {
            "success": True,
            "data": export_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
