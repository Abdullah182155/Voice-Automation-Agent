import pyaudio
import wave
import os
from gtts import gTTS
import pygame
import time
from datetime import datetime

# For faster-whisper
from faster_whisper import WhisperModel
from dotenv import load_dotenv

load_dotenv()

# Configuration for faster-whisper
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE")
# Device to use for inference ("cuda" or "cpu").
# If you have a GPU, "cuda" is much faster. Otherwise, use "cpu".
# If you don't have CUDA installed or it's not detected, it will fall back to CPU.
DEVICE = "cuda" if os.getenv("WHISPER_DEVICE", "cpu") == "cuda" else "cpu" 
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8" # "float16" for GPU, "int8" for CPU for efficiency


print(f"Loading Whisper model '{WHISPER_MODEL_SIZE}' on {DEVICE} with {COMPUTE_TYPE} compute type...")
try:
    # Model will be downloaded if not available locally
    model = WhisperModel(WHISPER_MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    print("Please ensure you have the necessary dependencies for faster-whisper (e.g., CUDA if using GPU).")
    print("Falling back to CPU if an issue occurred with CUDA setup.")
    # Try falling back to CPU if there was a CUDA issue
    try:
        model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        DEVICE = "cpu"
        COMPUTE_TYPE = "int8"
        print("Whisper model loaded successfully on CPU as a fallback.")
    except Exception as e_fallback:
        print(f"Critical error: Could not load Whisper model even on CPU: {e_fallback}")
        model = None # Indicate failure to load model


# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000 # Whisper expects 16kHz sample rate
CHUNK = 512
RECORD_MAX_SECONDS = 20 # Maximum recording duration if no activity detected
SILENCE_THRESHOLD = 200 # Adjust as needed (lower for more sensitive, higher for less sensitive)
SILENCE_CHUNKS_LIMIT = 2 * (RATE // CHUNK) # 2 seconds of silence to stop recording

def record_audio(output_filename="user_input.wav"):
    """
    Records audio from the microphone with basic voice activity detection (VAD).
    Stops recording after a period of silence or max duration.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening (Whisper mode)... Please speak now.")
    frames = []
    silence_chunks = 0
    start_time = time.time()

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False) # Capture overflow
        frames.append(data)
        
        # Simple RMS-based silence detection
        # Sum of squares to get power, then average
        current_volume = sum(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) for i in range(0, len(data), 2)) // (CHUNK // 2)
        
        if current_volume < SILENCE_THRESHOLD:
            silence_chunks += 1
        else:
            silence_chunks = 0 # Reset silence counter if speech is detected

        if time.time() - start_time > RECORD_MAX_SECONDS:
            print("Max recording duration reached.")
            break
        
        if silence_chunks > SILENCE_CHUNKS_LIMIT and len(frames) > SILENCE_CHUNKS_LIMIT * 2: # Ensure some initial speech was captured
            print("Silence detected, stopping recording.")
            break
        
    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    if not frames:
        print("No audio recorded.")
        return None

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    return output_filename

def listen_to_user_whisper():
    """
    Listens to user's voice input and converts it to text using faster-whisper.
    Returns the transcribed text or None if an error occurs.
    """
    if not model:
        print("Whisper model not loaded. Cannot perform STT.")
        return None

    audio_file = record_audio()
    if not audio_file:
        return None

    try:
        segments, info = model.transcribe(audio_file, beam_size=5) # beam_size can be adjusted
        
        full_transcript = []
        for segment in segments:
            full_transcript.append(segment.text)
        
        os.remove(audio_file) # Clean up the audio file
        
        if full_transcript:
            text = " ".join(full_transcript).strip()
            print(f"You said: \"{text}\"")
            return text
        else:
            print("Whisper STT: No speech detected or transcribed.")
            return None
    except Exception as e:
        print(f"Error during faster-whisper transcription: {e}")
        if os.path.exists(audio_file):
            os.remove(audio_file) # Ensure cleanup even on error
        return None

def speak_response(text):
    """
    Converts text to speech and plays it to the user.
    """
    print(f"Agent says: \"{text}\"")
    try:
        tts = gTTS(text=text, lang='en')
        filename = "response.mp3"
        tts.save(filename)

        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(1)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        os.remove(filename) # Clean up the audio file
    except Exception as e:
        print(f"Error playing audio response: {e}")
        print("Please ensure you have an active internet connection for gTTS and proper audio device setup.")

# Override the original listen_to_user with the new Whisper version
listen_to_user = listen_to_user_whisper

if __name__ == "__main__":
    # Example usage:
    speak_response("Hello, how can I help you today using Whisper speech recognition?")
    user_input = listen_to_user()
    if user_input:
        speak_response(f"You just said: {user_input}. Is that correct?")