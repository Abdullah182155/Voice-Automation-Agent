# Voice Automation Agent

A clean, structured voice automation agent for appointment management with natural language processing and multi-source integration.

## 🚀 Features

- **Voice Recognition**: OpenAI Whisper for accurate speech-to-text
- **Natural Language Processing**: Claude 3.5 Sonnet for intent recognition
- **Text-to-Speech**: Google TTS for natural responses
- **Appointment Management**: Book, cancel, and list appointments
- **External API Integration**: Connect with scheduling services
- **Calendar Integration**: Sync with calendar systems
- **Current Date Handling**: Smart relative date processing

## 📁 Project Structure

```
voice-automation-agent/
├── voice_agent.py              # Main application
├── config.py                   # Configuration management
├── demo.py                     # Demo script
├── test.py                     # Test script
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
├── .env                        # Environment variables
├── data/                       # Data storage
│   ├── schedules.json         # Local appointments
│   └── calendar_events.json   # Calendar events
├── prompts/                    # LLM prompts
│   ├── system_prompt.txt      # System prompt
│   └── user_prompt_template.txt # User prompt template
└── utils/                      # Core modules
    ├── scheduler.py           # Local appointment management
    ├── speech_io.py           # Speech recognition/TTS
    ├── llm_interface.py       # LLM integration
    ├── api_client.py          # External API integration
    ├── calendar_integration.py # Calendar system
    ├── validation.py          # Input validation
    ├── logger.py              # Logging system
    └── managers.py            # Manager classes
```

## 🛠️ Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   Create `.env` file:
   ```env
   OPENROUTER_API_KEY=your_api_key_here
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   api_url=https://openrouter.ai/api/v1/chat/completions
   WHISPER_MODEL_SIZE=base
   WHISPER_DEVICE=cpu
   ```

3. **Get API keys**
   - Sign up at [OpenRouter](https://openrouter.ai/) for LLM access

## 🎯 Usage

### Run the Agent
```bash
python voice_agent.py
```

### Test the System
```bash
python test.py
```

### See Demo
```bash
python demo.py
```

## 🗣️ Voice Commands

### Booking Appointments
- "Book a doctor appointment for tomorrow at 2 PM"
- "Schedule a meeting with John next Monday at 10 AM"
- "I need to book a dentist appointment for December 15th at 3 PM"

### Canceling Appointments
- "Cancel my appointment with Dr. Smith"
- "Cancel appointment ID 5"
- "Remove my meeting tomorrow"

### Listing Appointments
- "Show me my appointments"
- "What appointments do I have today?"
- "List my schedule for this week"

## 🔧 Configuration

### Environment Variables
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_MODEL`: LLM model (default: claude-3.5-sonnet)
- `WHISPER_MODEL_SIZE`: Whisper model size (default: base)
- `WHISPER_DEVICE`: Processing device (cpu/cuda)

### Audio Requirements
- Microphone for voice input
- Speakers/headphones for voice output
- Internet connection for LLM and TTS services