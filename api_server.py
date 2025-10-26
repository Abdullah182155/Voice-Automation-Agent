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
        
        # Load existing appointments
        appointments = load_appointments()
        
        # Check for conflicts (same date and time)
        for existing_appt in appointments:
            if (existing_appt["date"] == appointment.date and 
                existing_appt["time"] == appointment.time):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Appointment slot {appointment.date} {appointment.time} is already booked"
                )
        
        # Create new appointment
        appointment_id = generate_appointment_id()
        confirmation_code = generate_confirmation_code()
        
        new_appointment = {
            "id": appointment_id,
            "date": appointment.date,
            "time": appointment.time,
            "description": appointment.description,
            "patient_name": appointment.patient_name or "Voice User",
            "contact_info": appointment.contact_info or "voice@example.com",
            "status": "confirmed",
            "booking_timestamp": datetime.now().isoformat(),
            "confirmation_code": confirmation_code
        }
        
        # Save appointment
        appointments.append(new_appointment)
        save_appointments(appointments)
        
        return AppointmentResponse(
            success=True,
            appointment_id=appointment_id,
            confirmation_code=confirmation_code,
            appointment=new_appointment,
            message="Appointment successfully booked"
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
        appointments = load_appointments()
        
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
        appointments = load_appointments()
        
        # Find and remove appointment
        for i, appt in enumerate(appointments):
            if appt["id"] == appointment_id:
                appointments.pop(i)
                save_appointments(appointments)
                
                return CancelResponse(
                    success=True,
                    appointment_id=appointment_id,
                    message="Appointment successfully canceled"
                )
        
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

@app.get("/api/appointments/health", summary="API Health Check")
async def health_check():
    """Detailed health check."""
    appointments = load_appointments()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_appointments": len(appointments),
        "api_version": "1.0.0"
    }

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
