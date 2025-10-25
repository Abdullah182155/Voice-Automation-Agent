#!/usr/bin/env python3
"""
Test script for Voice Automation Agent
Tests core functionality and configuration.
"""

import os
import json
from datetime import datetime

def test_imports():
    """Test if core modules can be imported."""
    print("Testing imports...")
    
    try:
        import config
        print("+ config module")
    except Exception as e:
        print(f"X config module: {e}")
        return False
    
    try:
        from utils import scheduler, validation, logger
        print("+ utils modules")
    except Exception as e:
        print(f"X utils modules: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration."""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        config = Config()
        
        # Test date info
        date_info = config.get_date_info()
        print(f"+ Current date: {date_info['current_date']}")
        print(f"+ Current time: {date_info['current_time']}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_validation():
    """Test validation functions."""
    print("\nTesting validation...")
    
    try:
        from utils import DateValidator, TimeValidator
        
        # Test date validation
        valid_date = DateValidator.validate_date_format("2024-12-01")
        invalid_date = DateValidator.validate_date_format("invalid")
        
        print(f"✓ Date validation: {valid_date} (valid), {invalid_date} (invalid)")
        
        # Test time validation
        valid_time = TimeValidator.validate_time_format("14:30")
        invalid_time = TimeValidator.validate_time_format("25:00")
        
        print(f"✓ Time validation: {valid_time} (valid), {invalid_time} (invalid)")
        
        return True
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False

def test_scheduler():
    """Test scheduler functionality."""
    print("\nTesting scheduler...")
    
    try:
        from utils import add_appointment, list_appointments, cancel_appointment
        
        # Test adding appointment
        today = datetime.now().strftime("%Y-%m-%d")
        appt = add_appointment(today, "10:00", "Test appointment")
        
        if appt:
            print(f"✓ Added appointment: {appt['id']}")
            
            # Test listing
            appointments = list_appointments()
            print(f"✓ Listed appointments: {len(appointments)} characters")
            
            # Test cancellation
            success = cancel_appointment(appointment_id=appt['id'])
            print(f"✓ Cancellation: {success}")
        else:
            print("✗ Failed to add appointment")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Scheduler test failed: {e}")
        return False

def test_project_structure():
    """Test project structure."""
    print("\nTesting project structure...")
    
    required_files = [
        "voice_agent.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "utils/scheduler.py",
        "utils/validation.py",
        "utils/logger.py",
        "prompts/system_prompt.txt",
        "prompts/user_prompt_template.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True

def main():
    """Run all tests."""
    print("VOICE AUTOMATION AGENT - TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Validation", test_validation),
        ("Scheduler", test_scheduler),
        ("Project Structure", test_project_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print(" TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:15} : {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The agent is ready.")
        print("\nNext steps:")
        print("1. Configure API keys in .env file")
        print("2. Run: python voice_agent.py")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check the errors above.")

if __name__ == "__main__":
    main()
