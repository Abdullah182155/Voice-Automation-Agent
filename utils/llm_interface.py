import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

def get_llm_response(user_input_text):
    """
    Sends the user's query to the OpenRouter LLM and returns the structured JSON response.
    """
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not set in .env")
        return None

    api_url = os.getenv("api_url")

    # Get current datetime for dynamic date handling
    from datetime import datetime
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("prompts/system_prompt.txt", "r") as f:
        system_prompt = f.read()
    with open("prompts/user_prompt_template.txt", "r") as f:
        user_prompt_template = f.read()

    # Replace placeholders with actual values
    system_prompt = system_prompt.replace("{current_datetime}", current_datetime)
    formatted_user_prompt = user_prompt_template.replace("{user_query}", user_input_text)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "Voice Automation Agent", # App Name
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_user_prompt}
        ],
        "max_tokens": 150, # Increased for potentially longer descriptions/responses
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        print(f"DEBUG: Raw response from OpenRouter: {response.text}")
        response_data = response.json()
        
        # Extract content from the LLM's response
        llm_content = response_data['choices'][0]['message']['content']
        print(f"LLM Raw Response Content: {llm_content}")

        # Attempt to parse the LLM's content as JSON
        try:
            structured_response = json.loads(llm_content)
            return structured_response
        except json.JSONDecodeError:
            print("Warning: LLM response was not valid JSON. Attempting a fallback parse.")
            return {"intent": "fallback", "original_llm_response": llm_content} # Indicate parsing failure
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with OpenRouter API: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in LLM communication: {e}")
        return None

def keyword_fallback_parser(text):
    """
    A simple keyword-based parser for basic intent detection if LLM fails.
    """
    text_lower = text.lower()
    if "book" in text_lower or "schedule" in text_lower or "add" in text_lower:
        return {"intent": "book_schedule", "description": text}
    elif "cancel" in text_lower or "delete" in text_lower or "remove" in text_lower:
        return {"intent": "cancel_schedule", "description": text}
    elif "list" in text_lower or "show" in text_lower or "appointments" in text_lower or "meetings" in text_lower:
        return {"intent": "get_schedule", "description": text}
    else:
        return {"intent": "unknown", "description": text}

if __name__ == "__main__":
    # Test LLM integration
    print("Testing LLM with 'Book a meeting for next Tuesday at 10 AM regarding the Q3 report.'")
    llm_output = get_llm_response("Book a meeting for next Tuesday at 10 AM regarding the Q3 report.")
    print(f"LLM Output: {json.dumps(llm_output, indent=2)}")

    print("\nTesting LLM with 'Cancel the appointment about project Alpha on Friday.'")
    llm_output = get_llm_response("Cancel the appointment about project Alpha on Friday.")
    print(f"LLM Output: {json.dumps(llm_output, indent=2)}")

    print("\nTesting LLM with 'Show me all my appointments.'")
    llm_output = get_llm_response("Show me all my appointments.")
    print(f"LLM Output: {json.dumps(llm_output, indent=2)}")

    print("\nTesting keyword fallback with 'I want to see my schedule.'")
    fallback_output = keyword_fallback_parser("I want to see my schedule.")
    print(f"Fallback Output: {json.dumps(fallback_output, indent=2)}")

    print("\nTesting keyword fallback with 'I need to add an event.'")
    fallback_output = keyword_fallback_parser("I need to add an event.")
    print(f"Fallback Output: {json.dumps(fallback_output, indent=2)}")