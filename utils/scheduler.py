import json
import os
from datetime import datetime, timedelta

SCHEDULE_FILE = "data/schedules.json"

def _load_schedules():
    """Loads schedules from the JSON file."""
    if not os.path.exists(SCHEDULE_FILE) or os.path.getsize(SCHEDULE_FILE) == 0:
        return []
    with open(SCHEDULE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {SCHEDULE_FILE} is corrupted or empty. Starting with an empty list.")
            return []

def _save_schedules(schedules):
    """Saves schedules to the JSON file."""
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedules, f, indent=4)

def _get_next_id(schedules):
    """Generates a unique incremental ID for a new appointment."""
    if not schedules:
        return 1
    return max(schedule['id'] for schedule in schedules) + 1

def add_appointment(date_str, time_str, description):
    """
    Adds a new appointment to the schedule.
    Expects date_str in 'YYYY-MM-DD' and time_str in 'HH:MM' format.
    Returns the new appointment details or None if invalid.
    """
    schedules = _load_schedules()
    try:
        # Validate date and time format
        full_datetime_str = f"{date_str} {time_str}"
        datetime_obj = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date or time format provided for booking.")
        return None

    new_id = _get_next_id(schedules)
    new_appointment = {
        "id": new_id,
        "date": date_str,
        "time": time_str,
        "description": description,
        "timestamp": datetime_obj.isoformat()
    }
    schedules.append(new_appointment)
    _save_schedules(schedules)
    return new_appointment

def find_appointments(query_date=None, query_description=None, fuzzy_match=False):
    """
    Finds appointments based on date, description, or both.
    If fuzzy_match is True, it will search for description substrings.
    Returns a list of matching appointments.
    """
    schedules = _load_schedules()
    found_appointments = []

    for appt in schedules:
        match_date = True
        match_description = True

        if query_date:
            try:
                # Allow partial date matching for listing (e.g., 'tomorrow', 'next week')
                appt_date = datetime.strptime(appt['date'], "%Y-%m-%d").date()
                if isinstance(query_date, datetime):
                    match_date = (appt_date == query_date.date())
                elif isinstance(query_date, str):
                    # Basic string matching for now, could be enhanced with date parsing for "tomorrow", "next week"
                    match_date = (query_date in appt['date'])
            except ValueError:
                match_date = False # Invalid date in stored data

        if query_description:
            if fuzzy_match:
                match_description = query_description.lower() in appt['description'].lower()
            else:
                match_description = query_description.lower() == appt['description'].lower()

        if match_date and match_description:
            found_appointments.append(appt)
    
    # Sort appointments by timestamp
    found_appointments.sort(key=lambda x: datetime.fromisoformat(x['timestamp']))
    return found_appointments

def cancel_appointment(appointment_id=None, description=None, date=None):
    """
    Cancels an appointment by ID, or by description and date if ID is not provided.
    Returns the canceled appointment or None if not found/canceled.
    """
    schedules = _load_schedules()
    initial_count = len(schedules)
    
    if appointment_id:
        schedules = [appt for appt in schedules if appt['id'] != appointment_id]
        if len(schedules) < initial_count:
            _save_schedules(schedules)
            return True # Successfully canceled by ID
        else:
            return False # ID not found
    elif description and date:
        # Find by description and date for confirmation
        matching_appointments = [
            appt for appt in schedules
            if appt['description'].lower() == description.lower() and appt['date'] == date
        ]
        if matching_appointments:
            # For simplicity, cancel the first one found if multiple exist for same description/date
            appt_to_cancel = matching_appointments[0]
            schedules.remove(appt_to_cancel)
            _save_schedules(schedules)
            return appt_to_cancel # Return the canceled appointment
        else:
            return False # No matching appointment found
    return False # Insufficient details to cancel

def list_appointments(date_filter=None):
    """
    Lists appointments, optionally filtering by date.
    date_filter can be 'today', 'tomorrow', 'week', 'month', or None for all.
    Returns a natural language summary.
    """
    schedules = _load_schedules()
    
    now = datetime.now()
    filtered_schedules = []

    if date_filter == 'today':
        filtered_schedules = [
            appt for appt in schedules
            if datetime.strptime(appt['date'], "%Y-%m-%d").date() == now.date()
        ]
    elif date_filter == 'tomorrow':
        tomorrow = now + timedelta(days=1)
        filtered_schedules = [
            appt for appt in schedules
            if datetime.strptime(appt['date'], "%Y-%m-%d").date() == tomorrow.date()
        ]
    elif date_filter == 'week':
        # Appointments from today up to 7 days from now
        end_of_week = now + timedelta(days=7)
        filtered_schedules = [
            appt for appt in schedules
            if now.date() <= datetime.strptime(appt['date'], "%Y-%m-%d").date() <= end_of_week.date()
        ]
    elif date_filter == 'month':
        # Appointments for the current month
        filtered_schedules = [
            appt for appt in schedules
            if datetime.strptime(appt['date'], "%Y-%m-%d").month == now.month and
               datetime.strptime(appt['date'], "%Y-%m-%d").year == now.year
        ]
    else: # All appointments
        filtered_schedules = schedules

    if not filtered_schedules:
        return "You have no appointments scheduled." if date_filter else "You have no upcoming appointments."

    # Sort appointments by date and time
    filtered_schedules.sort(key=lambda x: datetime.strptime(f"{x['date']} {x['time']}", "%Y-%m-%d %H:%M"))

    summary = []
    for appt in filtered_schedules:
        appt_datetime = datetime.strptime(f"{appt['date']} {appt['time']}", "%Y-%m-%d %H:%M")
        date_display = "today" if appt_datetime.date() == now.date() else \
                       "tomorrow" if appt_datetime.date() == (now + timedelta(days=1)).date() else \
                       appt_datetime.strftime("%A, %B %d, %Y")
        summary.append(f"- ID {appt['id']}: '{appt['description']}' on {date_display} at {appt['time']}.")
    
    if date_filter == 'today':
        return "Here are your appointments for today:\n" + "\n".join(summary)
    elif date_filter == 'tomorrow':
        return "Here are your appointments for tomorrow:\n" + "\n".join(summary)
    elif date_filter == 'week':
        return "Here are your appointments for the coming week:\n" + "\n".join(summary)
    elif date_filter == 'month':
        return "Here are your appointments for this month:\n" + "\n".join(summary)
    else:
        return "Here are all your scheduled appointments:\n" + "\n".join(summary)

if __name__ == "__main__":
    # Test cases for scheduler functions
    # Ensure data/schedules.json is empty or contains an empty array [] before running tests
    
    print("--- Scheduler Tests ---")

    # Add appointments
    print("\nAdding appointments...")
    appt1 = add_appointment("2023-10-26", "10:00", "Discuss project Alpha")
    appt2 = add_appointment("2023-10-27", "14:30", "Team sync meeting")
    appt3 = add_appointment("2023-10-26", "16:00", "Client call with Beta Inc.")
    print(f"Added: {appt1}")
    print(f"Added: {appt2}")
    print(f"Added: {appt3}")

    # List all appointments
    print("\nListing all appointments:")
    print(list_appointments())

    # List appointments for a specific date (e.g., today or tomorrow for dynamic testing)
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\nListing appointments for {today_str} (today):")
    print(list_appointments(date_filter='today')) # This assumes some test data is for today or tomorrow

    # Find appointment by description
    print("\nFinding 'Team sync meeting':")
    found = find_appointments(query_description="Team sync meeting", fuzzy_match=False)
    print(f"Found: {found}")

    # Cancel appointment by ID
    if appt1:
        print(f"\nCanceling appointment with ID {appt1['id']}...")
        canceled_success = cancel_appointment(appointment_id=appt1['id'])
        print(f"Canceled by ID success: {canceled_success}")
        print("\nAppointments after cancellation:")
        print(list_appointments())

    # Add one more to test cancel by description/date
    appt_to_cancel = add_appointment("2023-10-28", "11:00", "Review quarterly performance")
    print(f"Added for cancellation test: {appt_to_cancel}")
    
    if appt_to_cancel:
        print(f"\nCanceling appointment '{appt_to_cancel['description']}' on {appt_to_cancel['date']}...")
        canceled_appt_details = cancel_appointment(description=appt_to_cancel['description'], date=appt_to_cancel['date'])
        print(f"Canceled by description/date: {canceled_appt_details}")
        print("\nAppointments after second cancellation:")
        print(list_appointments())

    # Clean up (optional)
    #_save_schedules([])
    print("\nCleaned up schedules.json")