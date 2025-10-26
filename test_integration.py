#!/usr/bin/env python3
"""
Integration Test Script
Tests the integration between API appointments, calendar events, and schedules.
"""

import json
import sys
import os
from datetime import datetime, timedelta

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

def test_integration():
    """Test the data integration system."""
    print("=" * 60)
    print("TESTING DATA INTEGRATION SYSTEM")
    print("=" * 60)
    
    try:
        from data_integration import integration_manager
        
        # Test 1: Get current state
        print("\n1. Getting current appointments from all systems...")
        all_appointments = integration_manager.get_all_appointments()
        print(f"Found {len(all_appointments)} appointments across all systems")
        
        for appt in all_appointments:
            print(f"  - {appt.description} on {appt.date} at {appt.time} (Source: {appt.source})")
        
        # Test 2: Add new appointment to all systems
        print("\n2. Adding new appointment to all systems...")
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        test_appointment = {
            "date": future_date,
            "time": "14:00",
            "description": "Integration Test Appointment",
            "patient_name": "Test User",
            "contact_info": "test@example.com"
        }
        
        results = integration_manager.add_appointment_to_all_systems(test_appointment)
        print("Results:")
        for system, result in results.items():
            print(f"  - {system}: {result}")
        
        # Test 3: Verify appointment was added
        print("\n3. Verifying appointment was added...")
        updated_appointments = integration_manager.get_all_appointments()
        print(f"Now found {len(updated_appointments)} appointments")
        
        # Test 4: Get unified summary
        print("\n4. Getting unified summary...")
        summary = integration_manager.get_unified_appointments_summary()
        print(summary)
        
        # Test 5: Sync systems
        print("\n5. Synchronizing all systems...")
        sync_results = integration_manager.sync_all_systems()
        print(f"Sync completed. Found {len(sync_results.get('conflicts', []))} conflicts.")
        
        # Test 6: Export all data
        print("\n6. Exporting all data...")
        export_data = integration_manager.export_all_data()
        print(f"Export contains:")
        print(f"  - {len(export_data['schedules'])} schedule entries")
        print(f"  - {len(export_data['calendar_events'])} calendar events")
        print(f"  - {len(export_data['api_appointments'])} API appointments")
        print(f"  - {len(export_data['unified_appointments'])} unified appointments")
        
        print("\n" + "=" * 60)
        print("INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_server():
    """Test the API server endpoints."""
    print("\n" + "=" * 60)
    print("TESTING API SERVER ENDPOINTS")
    print("=" * 60)
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test health check
        print("\n1. Testing health check...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test booking appointment
        print("\n2. Testing appointment booking...")
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        booking_data = {
            "date": future_date,
            "time": "16:00",
            "description": "API Test Appointment",
            "patient_name": "API Test User",
            "contact_info": "apitest@example.com"
        }
        
        response = requests.post(f"{base_url}/api/appointments/book", json=booking_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Appointment ID: {result['appointment_id']}")
            print(f"Confirmation Code: {result['confirmation_code']}")
            appointment_id = result['appointment_id']
        else:
            print(f"Error: {response.text}")
            return False
        
        # Test getting appointments
        print("\n3. Testing get appointments...")
        response = requests.get(f"{base_url}/api/appointments")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['total_count']} appointments")
        
        # Test unified appointments
        print("\n4. Testing unified appointments...")
        response = requests.get(f"{base_url}/api/appointments/unified")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['total_count']} unified appointments")
        
        # Test sync
        print("\n5. Testing system sync...")
        response = requests.post(f"{base_url}/api/appointments/sync")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Sync completed: {result['message']}")
        
        # Test cancel appointment
        if 'appointment_id' in locals():
            print(f"\n6. Testing appointment cancellation...")
            response = requests.delete(f"{base_url}/api/appointments/{appointment_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Cancellation: {result['message']}")
        
        print("\n" + "=" * 60)
        print("API SERVER TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to API server.")
        print("Make sure the server is running with: python start_api_server.py")
        return False
    except Exception as e:
        print(f"\nERROR: API server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Starting comprehensive integration tests...")
    
    # Test data integration
    integration_success = test_integration()
    
    # Test API server (only if server is running)
    api_success = test_api_server()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Data Integration Test: {'PASSED' if integration_success else 'FAILED'}")
    print(f"API Server Test: {'PASSED' if api_success else 'FAILED'}")
    
    if integration_success and api_success:
        print("\n🎉 ALL TESTS PASSED! Integration is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    print("\nTo start the API server for testing:")
    print("python start_api_server.py")
    print("\nTo test with Postman, use the endpoints documented in POSTMAN_TESTING_GUIDE.md")

if __name__ == "__main__":
    main()
